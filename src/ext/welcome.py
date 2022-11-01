"""Cog for welcoming new members"""

import discord
from discord.ext import commands
from datetime import datetime

from constants import ChannelPurposes
from db import db
from . import BaseCog


class Welcome(BaseCog):
    """Cog for welcoming new members"""

    def __init__(self, bot):
        super().__init__(bot)

    async def _get_channel_from_purpose(
        self,
        guild_id:int,
        purpose_id:int
    ) -> discord.TextChannel | None:
        """Get a channel object"""

        channel_id = db.field(
            "SELECT channel_id FROM guild_channels " \
            "WHERE guild_id = ? AND purpose_id = ?",
            guild_id, purpose_id
        ) or 0  # Snowflake 0 is valid but NoneType is not
        channel = await self.bot.get.channel(channel_id)
        return channel

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        """Send a welcome message to the new member.

        Args:
            member (discord.Member): The new member.
        """

        channel = await self._get_channel_from_purpose(
            member.guild.id, ChannelPurposes.members_say_welcome.value
        )
        if channel:
            embed = await self.get_welcome_embed(member)
            await channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        """Sends a message when a member leaves the server

        Args:
            member (discord.Member): The member that left.
        """

        channel = await self._get_channel_from_purpose(
            member.guild.id, ChannelPurposes.members_say_goodbye.value
        )
        if channel:
            embed = await self.get_remove_embed(member)
            await channel.send(embed=embed)

    async def get_welcome_embed(
        self, member:discord.Member, /
    ) -> discord.Embed:
        """Returns a welcome embed for the passed user.

        Args:
            member (discord.Member): The member to welcome.

        Returns:
            discord.Embed: The welcome embed.
        """

        # The embed base
        embed = discord.Embed(
            title='Welcome to the server!',
            description=f'Thank you for joining {member.mention}!' \
                '\nPlease read the rules and enjoy your stay!',
            colour=discord.Colour.from_str('#00FEFE'),
            timestamp=datetime.now()
        )

        # Get the icon url footer if it exists
        try:
            icon_url = member.guild.icon.url
        except AttributeError:
            icon_url = None

        # Thumbnail and footer for the embed
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text='DCG Server', icon_url=icon_url)

        return embed

    async def get_remove_embed(self, member:discord.Member):
        """Returns a remove embed for the passed user.

        Args:
            member (discord.Member): _description_
        """

        # The embed base
        embed = discord.Embed(
            title='Goodbye, you won\'t be missed!',
            description=f'{member.name} has left the server.'
                '\nAllow me to reach for my tiny violin.',
            colour=discord.Colour.from_str('#00FEFE'),
            timestamp=datetime.now()
        )

        # Get the icon url footer if it exists
        try:
            icon_url = member.guild.icon.url
        except AttributeError:
            icon_url = None

        # Thumbnail and footer for the embed
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text='DCG Server', icon_url=icon_url)

        return embed


async def setup(bot):
    """Setup the welcome cog"""

    await bot.add_cog(Welcome(bot))
