""""""

import os
import time
import logging
from datetime import timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
from discord.ext import commands

from constants import ACTIVITY_MSG, ChannelPurposes
from db import db
from ._get import Get
from .cog_manager import CogManager


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
        self.get: Get = Get(self)

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

    async def sync_app_commands(self) -> None:
        """Sync app commands with discord"""

        log.info('Syncing App Commands')

        # Syncing requires a ready bot
        await self.wait_until_ready()

        if not self.commands_synced:
            await self.tree.sync()
            self.commands_synced = True
            log.info('App Commands Synced')

    async def send_logs(self, msg:str, include_file:bool=False) -> None:
        """Send a message to all purposed log channels

        Args:
            msg (str): The message to send.
            include_file (bool, optional): Whether to include the log file. Defaults to False.
        """

        log.info("Sending logs to all logging channels")

        log_channel_ids = db.column(
            "SELECT channel_id FROM guild_channels WHERE purpose_id = ?",
            ChannelPurposes.logs.value
        )

        log.debug(
            "Found %s logging channels, sending",
            len(log_channel_ids)
        )

        for channel_id in log_channel_ids:

            # Get the channel and send the message
            channel = await self.get.channel(channel_id)
            await channel.send(msg)

            # Follow up with a new log file if requested
            if include_file:
                filename = os.path.basename(self.log_filepath)
                file = discord.File(self.log_filepath, filename=filename)
                await channel.send(file=file)

    async def on_ready(self) -> None:
        """
        Called when the bot logs in.
        Syncs slash commands and prints a ready message.
        """

        # Sync app commands with discord
        await self.sync_app_commands()

        # Start the scheduler for db autosaving
        self.scheduler.start()

        log.info('Logged in as %s (ID: %s)', self.user, self.user.id)

        # Send a ready message to all logging channels
        await self.send_logs('**I\'m back online!**')

    async def close(self):
        """Handles the shutdown process of the bot"""

        log.info('Shutting down...')
        filename = os.path.basename(self.log_filepath)

        # Send a ready message to all logging channels
        await self.send_logs(
            'I\'m shutting down, here are the logs for this session.' \
            f'\nStarted: {filename[:-4]}\nUptime: {str(self.uptime)}',
            include_file=True
        )
        await super().close()

    async def load_cogs(self):
        """
        Attempts to load all .py files in the cogs directory as cogs.
        """

        # The cog manager is loaded seperately so that it can not be
        # unloaded because it is used to unload other cogs.
        cog_manager = CogManager(self)
        log.info('Loading %s', cog_manager.qualified_name)
        await self.add_cog(cog_manager)

        log.info('Loading cog files')

        for filename in os.listdir('./src/cogs'):

            # Skip non cog files
            if not filename.endswith('.py') or filename.startswith('_'):
                log.debug(
                    'Skipping non cog file %s in cogs directory',
                    filename
                )
                continue

            # Load the cog
            await self.load_extension(f'cogs.{filename[:-3]}')
            log.debug('Loading cog file: %s', filename)
