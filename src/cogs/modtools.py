"""Server Moderation Tools"""

import discord
from discord import (
    app_commands,
    Interaction as Inter
)

from ui import BanMemberModal
from . import BaseCog


class ModToolsCog(BaseCog, name="Moderation Tools"):
    """Cog for moderation tools"""

    @app_commands.command(name="kick")
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def kick_cmd(self, inter:Inter, member:discord.Member):
        """Kick a member from the server"""
        await inter.response.send_message(
            "dummy kick response"
        )

    @app_commands.command(name="ban")
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def ban_cmd(self, inter:Inter, member:discord.Member):
        """Ban a member from the server"""

        model = BanMemberModal(member)
        await inter.response.send_modal(model)

    @app_commands.command(name="mute")
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def mute_cmd(self, inter:Inter, member:discord.Member, minutes:int):
        """Mute a member in the server"""
        await inter.response.send_message(
            "dummy mute response"
        )


async def setup(bot):
    """Cog setup function"""

    cog = ModToolsCog(bot)
    await bot.add_cog(cog)
