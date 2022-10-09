"""Cog for reddit commands."""

import logging
from discord import app_commands, Interaction as Inter

from cog import BaseCog


log = logging.getLogger(__name__)


class RedditCog(BaseCog, name='Reddit'):
    """Cog for reddit commands."""

    def __init__(self, bot):
        super().__init__(bot)

    group = app_commands.Group(
        name='reddit',
        description='Contribution commands'
    )


async def setup(bot):
    """Setup function for the cog."""

    cog = RedditCog(bot)
    await bot.add_cog(cog)