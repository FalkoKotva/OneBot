import logging
from discord.ext import commands


log = logging.getLogger(__name__)


class BaseCog(commands.Cog):
    """A cog class that all cogs should inherit from."""

    def __init__(self, bot):
        super().__init__()
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Method called when the cog has been loaded.
        Logs a ready message.
        """

        log.info(f'Loaded Cog (NAME: {self.qualified_name})')
