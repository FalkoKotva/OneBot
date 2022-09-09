"""
Cog for handling tickets.
"""


import aiosqlite
import discord
from discord import app_commands

from cog import Cog
from constants import DATABASE, GUILD_ID, TICKET_SUBMITTED


guild = discord.Object(GUILD_ID)


class Tickets(Cog):
    """
    Cog for handling tickets.
    """

    def __init__(self, bot):
        super().__init__(bot)

    @app_commands.command(name='report-ticket')
    @app_commands.guilds(guild)
    async def create_ticket(self, interaction: discord.Interaction, offender:discord.Member, *, reason: str):
        """
        Create a report ticket. Use this if another user has broken
        the rules or is harassing you.
        """
        
        await interaction.response.defer()

        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(
                """
                INSERT INTO user_report_tickets (userId, offenderUserId, messageContent) 
                VALUES (?, ?, ?)
                """,
                (interaction.user.id, offender.id, reason)
            )
            await db.commit()
            
            ticket_id = await db.execute_fetchall("SELECT * FROM user_report_tickets")
            ticket_id = ticket_id[-1][0]

        guild: discord.Guild = self.bot.main_guild
        print('guild', guild)
        category: discord.CategoryChannel = discord.Object(id=1017881107930304533)
        print('category', category)
        try:
            channel = await guild.create_text_channel(name="ticket")
        except Exception as e:
            print(e)
        print('channel', channel)

        await interaction.followup.send(TICKET_SUBMITTED)
        
        
    


async def setup(bot):
    """
    Setup function.
    Required for all cog files.
    Used by the bot to load this cog.
    """

    cog = Tickets(bot)
    await bot.add_cog(cog, guilds=(bot.main_guild,))
