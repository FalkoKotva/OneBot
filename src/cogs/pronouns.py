"""Extension for pronoundb integration"""

import logging

import httpx
import discord
from discord import (
    app_commands,
    Interaction as Inter
)

from . import BaseCog


class PronounCog(BaseCog, name="Pronouns"):
    """Cog for pronoundb integration"""

    __slots__ = ()

    def __init__(self, bot):
        super().__init__(bot)

        # Context menu version of get cmd
        get_menu = app_commands.ContextMenu(
            name="Get Pronouns",
            callback=self.get_pronouns_ctxmenu,
        )
        self.bot.tree.add_command(get_menu)

    def human_readable(self, pronouns_short:str, /) -> str:
        """Returns a human readable version of the pronouns"""

        pronoun_map = {
            "unspecified": "Unspecified, (this could be because they haven't set their pronouns yet)",
            "hh": "he/him",
            "hi": "he/it",
            "hs": "he/she",
            "ht": "he/they",
            "ih": "it/him",
            "ii": "it/its",
            "is": "it/she",
            "it": "it/they",
            "shh": "she/he",
            "sh": "she/her",
            "si": "she/it",
            "st": "she/they",
            "th": "they/he",
            "ti": "they/it",
            "ts": "they/she",
            "tt": "they/them",
            "any": "Any pronouns",
            "other": "Other pronouns",
            "ask": "Ask me my pronouns",
            "avoid": "Avoid pronouns, use my name"
        }

        return pronoun_map[pronouns_short]

    async def get_pronouns(self, member:discord.Member, /) -> str:
        """Get the pronouns of a member as a string"""

        url = "https://pronoundb.org/api/v1/lookup"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{url}?platform=discord&id={member.id}"
            )

        pronouns_short = response.json()["pronouns"]
        return self.human_readable(pronouns_short)

    group = app_commands.Group(
        name="pronouns",
        description="PronounDB Integration Commands"
    )

    @group.command(name="get")
    async def get_pronouns_cmd(self, inter:Inter, member:discord.Member):
        """Get the pronouns of a member"""

        pronouns = await self.get_pronouns(member)

        await inter.response.send_message(
            f"{member.mention} pronouns are {pronouns}",
            ephemeral=True
        )

    async def get_pronouns_ctxmenu(self, inter:Inter, member:discord.Member):
        """Get the pronouns of a member"""

        pronouns = await self.get_pronouns(member)

        await inter.response.send_message(
            f"{member.mention} pronouns are {pronouns}",
            ephemeral=True
        )


async def setup(bot):
    """Cog setup function"""

    await bot.add_cog(PronounCog(bot))
