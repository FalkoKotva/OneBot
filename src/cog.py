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
        self.bot: commands.Bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Method called when the cog has been loaded.
        Logs a ready message.
        """
        log.info(f'Loaded Cog (NAME: {self.__class__.__name__})')
