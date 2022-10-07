"""
Cog class for all cogs to inherit from
"""

import logging
from discord.ext import commands
from typing import Callable, Coroutine


log = logging.getLogger(__name__)


class Cog(commands.Cog):
    """
    A cog class that all cogs should inherit from.
    """

    def __init__(self, bot, post_ready:Callable=None, async_post_ready:Coroutine=None):
        super().__init__()
        self.bot: commands.Bot = bot
        self._post_ready = post_ready
        self._async_post_ready = async_post_ready
        
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Method called when the cog has been loaded.
        Logs a ready message.
        """
        log.info(f'Loaded Cog (NAME: {self.qualified_name})')

        if callable(self._post_ready):
            self._post_ready()

        if callable(self._async_post_ready):
            await self._async_post_ready()

        self._set_guild_commands()
    
    def _set_guild_commands(self):
        """Sets the guilds for all commands in the cog."""
        for command in self.get_app_commands():
            print(command.qualified_name)
            command._guild_ids = (self.bot.main_guild.id,)

