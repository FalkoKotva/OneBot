"""Misc commands extension."""

import logging

from discord import (
    app_commands,
    Interaction as Inter,
    Embed,
    Colour
)

from ui import MakeEmbedModal
from . import BaseCog

log = logging.getLogger(__name__)


class MiscCog(BaseCog, name="Misc Commands"):
    """Misc commands cog"""

    @app_commands.command(name="embed")
    async def embed_cmd(self, inter:Inter):
        """Send an embed"""

        async def do_embed(_inter, title, description, colour):
            embed = Embed(
                title=title,
                description=description,
                colour=Colour.from_str(colour) if colour else Colour.gold()
            )

            await _inter.followup.send(embed=embed)

        modal = MakeEmbedModal(coro=do_embed)
        await inter.response.send_modal(modal)


async def setup(bot):
    """Adds the cog to the bot."""

    await bot.add_cog(MiscCog(bot))
