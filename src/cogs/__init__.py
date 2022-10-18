"""Contains base cog for all cogs to inherit from."""

import logging

from discord.ext import commands


log = logging.getLogger(__name__)


class BaseCog(commands.Cog):
    """A cog class that all cogs should inherit from."""

    def __init__(self, bot):
        super().__init__()
        self.bot: commands.Bot = bot

    @commands.Cog.listener(name="on_ready")
    async def _on_ready(self):
        """
        Method called when the cog has been loaded.
        Logs a ready message.
        """

        log.info('Loaded Cog (NAME: %s)', self.qualified_name)
