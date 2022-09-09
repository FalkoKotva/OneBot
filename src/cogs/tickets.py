"""
Cog for handling tickets.
"""

import discord
from discord.ext import commands
from discord import app_commands

from cog import Cog
from constants import GUILD_ID


guild = discord.Object(GUILD_ID)


class Tickets(Cog):
    """
    Cog for handling tickets.
    """

    def __init__(self, bot):
        super().__init__(bot)

    @app_commands.command(name='ticket')
    @app_commands.guilds(guild)
    async def ticket(self, interaction: discord.Interaction):
        """
        Create a ticket
        """
        await interaction.response.send_message('Slash commands are working!')
        
    


async def setup(bot):
    """
    Setup function.
    Required for all cog files.
    Used by the bot to load this cog.
    """

    cog = Tickets(bot)
    await bot.add_cog(cog, guilds=(bot.main_guild,))
