"""Cog for welcoming new members"""

import discord
from discord import Interaction
from discord import app_commands
from discord.ext import commands
from datetime import datetime

from cog import Cog
from constants import GUILD_ID, Channels


class Welcome(Cog):
    """Cog for welcoming new members"""

    def __init__(self, bot):
        super().__init__(bot)

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        """Send a welcome message to the new member.

        Args:
            member (discord.Member): The new member.
        """

        embed = await self.get_welcome_embed(member)
        channel = self.bot.get_channel(Channels.WELCOME)
        await channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        """Sends a message when a member leaves the server

        Args:
            member (discord.Member): The member that left.
        """

        embed = await self.get_remove_embed(member)
        channel = self.bot.get_channel(Channels.WELCOME)
        await channel.send(embed=embed)
    
    group = app_commands.Group(
        name='wtest',
        description='Test the join/leave events',
        guild_ids=(GUILD_ID,),
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

        # Channels to be added to the embed
        rules_channel = self.bot.get_channel(Channels.RULES)
        roles_channel = self.bot.get_channel(Channels.ROLES)
        mental_channel = self.bot.get_channel(Channels.MENTAL_HEALTH)
        fhelp_channel = self.bot.get_channel(Channels.FIND_HELP)
        ticket_channel = self.bot.get_channel(Channels.ASK_TICKETS)
        ahelp_channel = self.bot.get_channel(Channels.ASK_HELP)

        # The embed base
        embed = discord.Embed(
            title='Welcome to the server!',
            description=f'Thank you for joining {member.mention}!' \
                '\nPlease read the rules and enjoy your stay!',
            colour=discord.Colour.from_str('#00FEFE'),
            timestamp=datetime.now()
        )

        # Add the fields
        embed.add_field(
            name='Where to Start',
            value=f'{rules_channel.mention}\
                \n{roles_channel.mention}',
        )
        embed.add_field(
            name='Need Help?',
            value=f'{mental_channel.mention}\
                \n{fhelp_channel.mention}'
        )
        embed.add_field(
            name='Contact Admins',
            value=f'{ticket_channel.mention}\
                \n{ahelp_channel.mention}'
        )

        # Thumbnail and footer for the embed
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text='DCG Server', icon_url=rules_channel.guild.icon.url)

        return embed

    async def get_remove_embed(self, member:discord.Member):
        """_summary_

        Args:
            member (discord.Member): _description_
        """
        
        # The embed base
        embed = discord.Embed(
            title='Goodbye, you won\'t be missed!',
            description=f'{member.mention} has left the server.',
            colour=discord.Colour.from_str('#00FEFE'),
            timestamp=datetime.now()
        )

        icon_url = self.bot.get_guild(GUILD_ID).icon.url

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
