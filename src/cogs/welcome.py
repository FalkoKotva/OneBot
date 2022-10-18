"""Cog for welcoming new members"""

import discord
from discord import Interaction
from discord import app_commands
from discord.ext import commands
from datetime import datetime

from . import BaseCog


class Welcome(BaseCog):
    """Cog for welcoming new members"""

    def __init__(self, bot):
        super().__init__(bot)
        self.welcome_channel_id = bot.config['guild']['channel_ids']['welcome']

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        """Send a welcome message to the new member.

        Args:
            member (discord.Member): The new member.
        """

        embed = await self.get_welcome_embed(member)
        channel = self.bot.get_channel(self.welcome_channel_id)
        await channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        """Sends a message when a member leaves the server

        Args:
            member (discord.Member): The member that left.
        """

        embed = await self.get_remove_embed(member)
        channel = self.bot.get_channel(self.welcome_channel_id)
        await channel.send(embed=embed)
    
    group = app_commands.Group(
        name='wtest',
        description='Test the join/leave events',
        default_permissions=discord.Permissions(moderate_members=True)
    )
    
    @group.command(name='join')
    async def welcome_test(self, interaction:Interaction, member:discord.Member):
        """Test command for the welcome view and embed"""

        # Get and send the embed
        embed = await self.get_welcome_embed(member)
        await interaction.channel.send(embed=embed)

        # Acknowledge the interaction to prevent an error
        await interaction.response.send_message('done')

    @group.command(name='remove')
    async def remove_test(self, inter:Interaction, member:discord.Member):
        """Test command for the remove embed"""

        # Get and send the embed
        embed = await self.get_remove_embed(member)
        await inter.channel.send(embed=embed)

        # Acknowledge the interaction to prevent an error
        await inter.response.send_message('done')

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

    await bot.add_cog(
        Welcome(bot),
        guilds=(bot.main_guild,)
    )
