"""Manage guild integration with the bot"""

import logging
import sqlite3

import discord
from discord import (
    app_commands,
    TextChannel,
    Interaction as Inter,
    Role
)

from db import db
from constants import ChannelPurposes, RolePurposes
from ui import ListConfiguredChannelsEmbed
from . import BaseCog


log = logging.getLogger(__name__)

def get_purposes(purpose_object, /) -> list[app_commands.Choice]:
    """Return a list of purposes"""
    return [
        app_commands.Choice(name=p.name, value=p.value)
        for p in purpose_object
    ]

def get_table(_object) -> str:
    """Get the applicable db table for the given object"""

    if isinstance(_object, TextChannel):
        return "guild_channels"
    elif isinstance(_object, Role):
        return "guild_roles"
    else:
        raise TypeError("Object must be a TextChannel or Role")


class GuildsCog(BaseCog, name="Guild Integrations"):
    """Cog for managing guild integration with the bot"""

    main_group = app_commands.Group(
        name="purpose",
        description="Manage guild integrations with the bot",
        default_permissions=discord.Permissions(moderate_members=True)
    )

    channel_group = app_commands.Group(
        parent=main_group,
        name="channels",
        description="Manage guild channels integration"
    )

    role_group = app_commands.Group(
        parent=main_group,
        name="roles",
        description="Manage guild roles integration"
    )

    def set_purpose(self, _object, purpose, /) -> bool:
        """Set the purpose of an object, returns bool if successful or not"""

        table = get_table(_object)

        try:
            db.execute(
                f"INSERT INTO {table} VALUES (?, ?, ?)",
                _object.id, _object.guild.id, purpose.value
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_purpose(self, _object, /) -> bool:
        """Clear the purpose of a given object"""

        table = get_table(_object)
        column_prefix = table.split("_")[1][:-1]
        assert column_prefix in ("channel", "role")

        db.execute(
            f"DELETE FROM {table} WHERE {column_prefix}_id = ?",
            _object.id
        )

    @channel_group.command(name="list")
    async def list_channels(self, inter:Inter):
        """List all configured guild channels"""

        data = db.records(
            "SELECT * FROM guild_channels WHERE guild_id = ?",
            inter.guild.id
        )

        if not data:
            await inter.response.send_message(
                "No channels are configured for this guild"
            )
            return

        embed = ListConfiguredChannelsEmbed(self.bot, data)
        await inter.response.send_message(embed=embed)

    @channel_group.command(name="set")
    @app_commands.choices(purpose=get_purposes(ChannelPurposes))
    async def add_channel(
        self,
        inter:Inter,
        channel:TextChannel,
        purpose:app_commands.Choice[int]
    ):
        """Set the purpose of a channel"""

        if self.set_purpose(channel, purpose):
            await inter.response.send_message(
                f"{channel.mention} has been purposed for {purpose.name}"
            )
        else:
            await inter.response.send_message(
                "This channel is already has a purpose"
            )

    @channel_group.command(name="remove")
    async def remove_channel(self, inter:Inter, channel:TextChannel):
        """Remove the purpose of a channel"""

        self.remove_purpose(channel)

        await inter.response.send_message(
            f"Channel {channel.mention} no longer has a purpose with me"
        )

    @role_group.command(name="set")
    @app_commands.choices(purpose=get_purposes(RolePurposes))
    async def add_role(self, inter:Inter, role:Role, purpose:app_commands.Choice[int]):
        """Set the purpose of a role"""

        if self.set_purpose(role, purpose):
            await inter.response.send_message(
                f"{role.mention} has been purposed for {purpose.name}"
            )
        else:
            await inter.response.send_message(
                "This role is already configured for a purpose"
            )

    @role_group.command(name="remove")
    async def remove_role(self, inter:Inter, role:Role):
        """Remove the purpose of a role"""

        self.remove_purpose(role)

        await inter.response.send_message(
            f"Channel {role.mention} is no longer configured"
        )


async def setup(bot):
    """Setup function for the cog"""

    cog = GuildsCog(bot)
    await bot.add_cog(cog)
