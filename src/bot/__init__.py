""""""

import os
import time
import logging
import discord
from discord import app_commands, Interaction as Inter
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import timedelta
from typing import Callable

from cogs import BaseCog
from utils import list_cogs, to_choices
from constants import ACTIVITY_MSG
from db import db


log = logging.getLogger(__name__)


class Bot(commands.Bot):
    """This class is the root of the bot."""

    # Discordpy doesnt automatically sync commands so we need a check
    commands_synced = False

    config: dict
    log_filepath: str

    def __init__(self, config:dict, log_filepath:str):
        """Initialize the bot.

        Args:
            config (dict): The config data.
            log_filepath (str): Log filepath for the current session.
        """

        self.config = config
        self.log_filepath = log_filepath

        # Scehdule the database autosaving
        self.scheduler = AsyncIOScheduler()
        db.autosave(self.scheduler)

        # Use this to roughly track the uptime
        self._start_time = time.time()

        # Setup the bot's intents
        intents = discord.Intents.all()
        super().__init__(command_prefix='ob ', intents=intents)

        # Set the bot's activity status
        self.activity = discord.Game(name=ACTIVITY_MSG)

        # Get the main discord server
        self.main_guild_id = config['guild']['id']
        self.main_guild = discord.Object(id=self.main_guild_id)

    @property
    def uptime(self) -> timedelta:
        """Returns the bot's uptime as a timedelta object"""

        difference = int(round(time.time() - self._start_time))
        return timedelta(seconds=difference)

    @property
    def start_time(self) -> str:
        """Returns the bot's start time as a string object"""

        _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self._start_time))
        return f'{_time}'

    async def sync_slash_commands(self):
        """Sync slash commands with discord"""

        log.info('Syncing App Commands')

        # Syncing requires a ready bot
        await self.wait_until_ready()

        if not self.commands_synced:
            await self.tree.sync()
            self.commands_synced = True
            log.info('App Commands Synced')

    async def on_ready(self):
        """
        Called when the bot logs in.
        Syncs slash commands and prints a ready message.
        """

        # Sync app commands
        await self.sync_slash_commands()

        # Start the scheduler
        self.scheduler.start()

        log.info(f'Logged in as {self.user} (ID: {self.user.id})')

        # Send a message into the discord log channel
        log_channel_id = self.config['guild']['channel_ids']['logs']
        log_channel = self.get_channel(log_channel_id)
        await log_channel.send('**I\'m back online!**')
    
    async def close(self):
        """Handles the shutdown process of the bot"""

        log.info(f'Shutting down...')
        filename = os.path.basename(self.log_filepath)

        # Create a discord file object
        file = discord.File(self.log_filepath, filename=filename)

        log_channel_id = self.config['guild']['channel_ids']['logs']

        # Send the log file to the logs channel
        log_channel = self.get_channel(log_channel_id)
        await log_channel.send(
            'I\'m shutting down, here are the logs for this session.'
            f'\nStarted: {filename[:-4]}\nUptime: {str(self.uptime)}',
        )
        await log_channel.send(file=file)

        file.close()
        await super().close()        

    async def load_cogs(self):
        """
        Attempts to load all .py files in the cogs directory as cogs.
        """
        
        # The cog manager is loaded seperately so that it can not be
        # unloaded because it is used to unload other cogs.
        cog_manager = CogManager(self)
        log.info(f'Loading {cog_manager.qualified_name}')
        await self.add_cog(cog_manager)

        log.info('Loading cog files')

        for filename in os.listdir('./src/cogs'):

            # Skip non cog files
            if not filename.endswith('.py') or filename.startswith('_'):
                log.debug(
                    f'Skipping non cog file {filename} in cogs directory'
                )
                continue

            # Load the cog
            await self.load_extension(f'cogs.{filename[:-3]}')
            log.debug(f'Loading cog file: {filename}')
            


class CogManager(BaseCog, name='Cog Manager'):
    """
    Cog manager is incharge of loading, unloading and reloading cogs.
    It is loaded seperately from other cogs so that it can not be
    unloaded.
    """

    def __init__(self, bot:commands.Bot):
        super().__init__(bot)
        self.group.guild_ids = (bot.main_guild.id)

    group = app_commands.Group(
        name='cog',
        description='Cog management commands',
        default_permissions=discord.Permissions(moderate_members=True)
    )
    
    async def _cog_command_wrapper(
        self,
        inter:Inter,
        cog:app_commands.Choice,
        action:str,
        func:Callable
    ) -> None:
        """Wrapper for using cog commands.
        Handles errors and sends a message.

        Args:
            inter (Inter): discord.Interaction object.
            cog (app_commands.Choice): the chosen cog.
            action (str): what action is being performed.
            func (Callable): the function to be called.
        """

        log.info(
            f'{inter.user.name}#{inter.user.discriminator} '
            f'({inter.user.id}) is {action}ing cog: {cog.name}'
        )

        await inter.response.defer(ephemeral=True)

        try:
            #
            self.bot.commands_synced = False
            await func()
            await self.bot.sync_slash_commands()

        except commands.ExtensionAlreadyLoaded:            
            # Action requires cog to be unloaded
            await inter.followup.send(
                f'Cog `{cog.name}` is already loaded',
                ephemeral=True
            )
            return

        except commands.ExtensionNotLoaded:
            # Action requires unloaded cog to be loaded
            await inter.followup.send(
                f'Cog `{cog.name}` is not loaded',
            )
            return

        except Exception as e:
            # If this ever happens then I will shit myself
            log.error(e.with_traceback())
            await inter.followup.send(
                'Something has gone terribly wrong, '
                'I\'ve logged the error... Good luck.'
            )
            return

        # Send a success message to the user
        await inter.followup.send(
            f'Cog `{cog.name}` {action} was successful!',
            ephemeral=True
        )

    @group.command(name='load')
    @app_commands.choices(cog=to_choices(list_cogs()))
    async def load_cog(
        self,
        inter:Inter,
        cog:app_commands.Choice[str]
    ):
        """Load one of the bots cogs."""

        async def _load():
            await self.bot.load_extension(f'cogs.{cog.name[:-3]}')

        await self._cog_command_wrapper(
            inter=inter,
            cog=cog,
            action='load',
            func=_load
        )

    @group.command(name='unload')
    @app_commands.choices(cog=to_choices(list_cogs()))
    async def unload_cog(
        self,
        inter:Inter,
        cog:app_commands.Choice[str]
    ):
        """Unload one of the bots cogs."""

        async def _unload():
            await self.bot.unload_extension(f'cogs.{cog.name[:-3]}')

        await self._cog_command_wrapper(
            inter=inter,
            cog=cog,
            action='unload',
            func=_unload
        )
    
    @group.command(name='reload')
    @app_commands.choices(cog=to_choices(list_cogs()))
    async def reload_cog(
        self,
        inter:Inter,
        cog:app_commands.Choice[str]
    ):
        """Reload one of the bots cogs"""

        async def _reload():
            await self.bot.reload_extension(f'cogs.{cog.name[:-3]}')

        await self._cog_command_wrapper(
            inter=inter,
            cog=cog,
            action='reload',
            func=_reload
        )

    @group.command(name='list')
    async def list_cogs(self, inter:Inter):
        """Responds with a list of all cogs."""
        
        output = '**List of cogs:**\n'
        cogs = self.bot.cogs.values()
        output += '\n'.join([cog.qualified_name for cog in cogs])
        await inter.response.send_message(output, ephemeral=True)
