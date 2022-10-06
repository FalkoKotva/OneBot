"""
Cog class for all cogs to inherit from
"""

import logging
from discord.ext import commands


log = logging.getLogger(__name__)


class Cog(commands.Cog):
    """
    A cog class that all cogs should inherit from.
    """

    def __init__(self, bot):
        super().__init__()
        self.bot: commands.Bot = bot
        self._set_guild_commands()
        
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Method called when the cog has been loaded.
        Logs a ready message.
        """
        log.info(f'Loaded Cog (NAME: {self.qualified_name})')
    
    def _set_guild_commands(self):
        """Sets the guilds for all commands in the cog."""
        for command in self.get_app_commands():
            command._guild_ids = (self.bot.main_guild.id,)

