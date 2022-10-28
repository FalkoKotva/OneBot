"""Server Moderation Tools"""

import logging
from datetime import datetime, timedelta, time

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


class ModToolsCog(BaseCog, name="Moderation Tools"):
    """Cog for moderation tools"""

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

    @app_commands.command(name="ban")
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def ban_cmd(
        self,
        inter:Inter,
        member:discord.Member,
        reason:str=None
    ):
        """Ban a member from the server"""

        await member.ban(reason=reason)
        await inter.response.send_message(f"Banned {member.name}")

    @app_commands.command(name="mute")
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.describe(
        member="The server member to mute",
        minutes="The amount of minutes to mute the member for",
        reason="The reason for the mute"
    )
    async def mute_cmd(
        self,
        inter:Inter,
        member:discord.Member,
        minutes:int=5,
        reason:str=None
    ):
        """Mute a member in the server"""

        log.info(
            "Muting %s for %s minutes in %s",
            member, minutes, inter.guild.name
        )

        mute_role_id = db.field(
            "SELECT role_id FROM guild_roles "
            "WHERE guild_id = ? AND purpose_id = ?",
            inter.guild.id, RolePurposes.muted.value
        )

        mute_role = inter.guild.get_role(mute_role_id)

        if not mute_role:
            log.debug("Mute role not found, cancelling mute")
            await inter.response.send_message(
                "There is no mute role configured for this server, "
                "use `/purpose roles` to configure one."
            )
            return

        log.debug("Mute role found, muting member")

        if mute_role in member.roles:
            log.debug("Member is already muted, cancelling mute")
            await inter.response.send_message(
                "This member is already muted."
            )
            return

        try:
            await member.add_roles(mute_role, reason=reason)
        except discord.Forbidden as err:
            log.error(err)
            await inter.response.send_message(content=err)
            return

        log.debug("Mute role added, scheduling unmute")

        now = datetime.now()
        end = now + timedelta(minutes=minutes)
        end = end.strftime(DATETIME_FORMAT)

        db.execute(
            "INSERT INTO guild_mutes "
            "(member_id, guild_id, reason, end_datetime) "
            "VALUES (?, ?, ?, ?)",
            member.id, inter.guild.id, reason, end
        )
        db.commit()

        await inter.response.send_message(
            f"Muted {member.name} for {minutes} minutes."
        )

    @tasks.loop(minutes=1)
    async def check_mute_task(self):
        """Check if mute timer has expired for each member"""

        log.debug("Checking mute timers")

        for guild in self.bot.guilds:

            log.debug("Checking mute timers in %s", guild.name)

            role_id = db.field(
                "SELECT role_id FROM guild_roles "
                "WHERE guild_id = ? AND purpose_id = ?",
                guild.id, RolePurposes.muted.value
            )

            role = guild.get_role(role_id)

            if not role:
                log.debug("No mute role found, skipping")
                continue

            for member in guild.members:

                if role not in member.roles:
                    continue

                try:
                    await member.remove_roles(role)
                except discord.Forbidden as err:
                    log.error(err)
                    continue

                log.debug("Unmuted %s, removing from db", member.name)

                db.execute(
                    "DELETE FROM guild_mutes "
                    "WHERE member_id = ? AND guild_id = ?",
                    member.id, guild.id
                )

        db.commit()
                


    @app_commands.command(name="see-muted")
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def see_muted_cmd(self, inter:Inter):
        """Get a list of all muted members"""

        muted_data = db.records(
            "SELECT member_id, reason, end_datetime FROM guild_mutes "
            "WHERE guild_id = ?",
            inter.guild_id
        )

        if not muted_data:
            await inter.response.send_message(
                "There are no muted members in this server."
            )
            return

        embed = ListMutedEmbed(self.bot, inter.guild, muted_data)
        await inter.response.send_message(embed=embed)


async def setup(bot):
    """Cog setup function"""

    cog = ModToolsCog(bot)
    await bot.add_cog(cog)
