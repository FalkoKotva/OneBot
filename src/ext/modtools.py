"""Server Moderation Tools"""

import logging
import sqlite3
from datetime import datetime, timedelta

import discord
from discord import (
    app_commands,
    Interaction as Inter
)
from discord.ext import tasks

from db import db
from ui import ListMutedEmbed
from constants import RolePurposes, DATETIME_FORMAT
from . import BaseCog


log = logging.getLogger(__name__)

def del_msg_choices():
    choices = [
        ("Don't Delete Any", 0),
        ("Previous Day", 1)
    ]
    choices.extend((f"Previous {i} Days", i) for i in range(2, 8))
    return [
        app_commands.Choice(name=name, value=val)
        for name, val in choices
    ]


class ModToolsCog(BaseCog, name="Moderation Tools"):
    """Cog for moderation tools"""

    async def validate_user(self, inter:Inter, member_or_id) -> discord.User | None:
        if type(member_or_id) is str:
            try:
                user = await self.bot.get.user(int(member_or_id))
            except (discord.NotFound, ValueError):
                user = None
        else:
            user = await self.bot.get.user(member_or_id.id)

        return user

    @app_commands.command(name="kick")
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def kick_cmd(
        self,
        inter:Inter,
        member:discord.Member,
        reason:str=None
    ):
        """Kick a member from the server"""

        await member.kick(reason=reason)
        await inter.response.send_message(f"Kicked {member.name}")

    # @app_commands.command(name="ban")
    # @app_commands.guild_only()
    # @app_commands.default_permissions(moderate_members=True)
    # async def ban_cmd(
    #     self,
    #     inter:Inter,
    #     member:discord.Member,
    #     reason:str=None
    # ):
    #     """Ban a member from the server"""

    #     await member.ban(reason=reason)
    #     await inter.response.send_message(f"Banned {member.name}")

    @app_commands.command(name="ban")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(ban_members=True)
    @app_commands.default_permissions(
        moderate_members=True,
        ban_members=True,
        kick_members=True
    )
    @app_commands.describe(
        user="The user to ban, this can be a mention or their ID",
        delete_messages="The amount of messages to delete from the user",
        reason="The reason for the ban"
    )
    @app_commands.choices(delete_messages=del_msg_choices())
    async def blacklist_cmd(
        self,
        inter:Inter,
        user:discord.User,
        delete_messages:app_commands.Choice[int],
        reason:str=None
    ):
        """Bans a user from this server, even if they aren't in it"""

        log.debug(
            "%s is banning %s from %s for \"%s\" and deleting their "
            "messages from the last %s days",
            inter.user, user, inter.guild, reason, delete_messages.value
        )

        username = f"{user.name}#{user.discriminator}"

        # Check if the user was already banned
        try:
            await inter.guild.fetch_ban(user)
            log.debug("%s was already banned, cancelling", username)
            await inter.response.send_message(
                f"{username} is already banned.",
                ephemeral=True
            )
            return

        except discord.NotFound:
            log.debug("%s was not banned, continue", username)


        await inter.guild.ban(
            user=user, reason=reason,
            delete_message_days=delete_messages.value
        )

        log.debug("Banned %s", username)

        await inter.response.send_message(
            f"I've just banned {username} from this server."
        ) 

async def setup(bot):
    """Cog setup function"""

    cog = ModToolsCog(bot)
    await bot.add_cog(cog)
