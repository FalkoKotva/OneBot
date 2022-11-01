"""Extension to provide help commands."""

import logging

import discord
from discord import (
    app_commands,
    Interaction as Inter
)
from discord.ext import commands

from ui import HelpSetPronounsEmbed, HelpGetPronounsEmbed
from . import BaseCog


log = logging.getLogger(__name__)


class HelpCog(BaseCog, name="Help Commands"):
    """Cog to provide help commands"""

    __slots__ = ()

    group = app_commands.Group(
        name="help",
        description="Get help with the bot"
    )

    @group.command(name="pronouns")
    async def pronoun_cmd(self, inter:Inter):
        """Get information about pronouns usage with the bot"""

        await inter.response.send_message(
            embeds=(
                HelpSetPronounsEmbed(),
                HelpGetPronounsEmbed()
            ),
            ephemeral=True
        )

    # @group.command(name="birthdays")
    async def birthday_cmd(self, inter:Inter):
        """Get information about birthday commands with the bot"""

        await inter.response.send_message(
            embeds=(
                # TODO: Add birthday help embed  
            ),
            ephemeral=True
        )


async def setup(bot):
    """Adds the cog to the bot."""

    cog = HelpCog(bot)
    await bot.add_cog(cog)
