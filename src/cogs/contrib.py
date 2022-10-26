"""Cog for contributing to the bot."""

import logging
from discord import app_commands, Interaction as Inter

from . import BaseCog


log = logging.getLogger(__name__)


class ContribCog(BaseCog, name='Contributions'):
    """Cog for contributing to the bot."""

    def __init__(self, bot):
        super().__init__(bot)

    group = app_commands.Group(
        name='contrib',
        description='Contribution commands'
    )

    @group.command(name='link')
    async def contribute(self, inter:Inter):
        """Link to contribute to the bot."""

        await inter.response.send_message(
            "https://github.com/XordK/OneBot",
            ephemeral=True
        )


async def setup(bot):
    """Setup function for the cog."""

    cog = ContribCog(bot)
    await bot.add_cog(cog)