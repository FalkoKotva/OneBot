"""Cog for contributing to the bot."""

import logging
from discord import app_commands, Interaction as Inter

from cog import BaseCog


class ContribCog(BaseCog, name='Contributions'):
    """Cog for contributing to the bot."""

    def __init__(self, bot):
        super().__init__(bot)

    group = app_commands.Group(
        name='contrib',
        description='Contribution commands'
    )

    @group.command(name='learn')
    async def contribute(self, inter:Inter):
        """Learn how to contribute to the bot."""

        await inter.response.send_message(
            'WIP',
            ephemeral=True
        )


async def setup(bot):
    """Setup function for the cog."""

    cog = ContribCog(bot)
    await bot.add_cog(cog)