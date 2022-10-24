"""Cog commands"""

import logging
from typing import Callable

import discord
from discord import app_commands
from discord import Interaction as Inter
from discord.ext import commands

from cogs import BaseCog
from utils import list_cogs, to_choices


log = logging.getLogger(__name__)


class CogManager(BaseCog, name='Cog Manager'):
    """
    Cog manager is incharge of loading, unloading and reloading cogs.
    It is loaded seperately from other cogs so that it can not be
    unloaded.
    """

    def __init__(self, bot:commands.Bot):
        super().__init__(bot)

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
            await self.bot.sync_app_commands()

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
