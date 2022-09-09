"""
Cog for handling tickets.
"""


import aiosqlite
import discord
from discord import app_commands

from cog import Cog
from constants import (
    DATABASE,
    GUILD_ID,
    TICKET_SUBMITTED,
    TICKETS_CATEGORY_ID
)


class Tickets(Cog):
    """
    Cog for handling tickets.
    """

    def __init__(self, bot):
        super().__init__(bot)

    group = app_commands.Group(name='ticket', description='Open tickets here...', guild_ids=(GUILD_ID,))

    async def create_ticket_channel(self, prefix:str, ticket_id:int) -> discord.TextChannel:
        """
        Creates and returns a discord TextChannel object to store a new ticket.
        """
        guild: discord.Guild = self.bot.get_guild(GUILD_ID)
        category: discord.CategoryChannel = discord.Object(id=TICKETS_CATEGORY_ID)
        return await guild.create_text_channel(name=f"{prefix}-ticket-{ticket_id}", category=category)

    @group.command(name='suggestion')
    async def create_suggestion_ticket(self, interaction:discord.Interaction, *, suggestion:str):
        """
        Suggest a feature for the server
        """
        
        # Show that the bot is thinking to prevent the interaction timing out
        await interaction.response.defer(ephemeral=True)

        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(
                """
                INSERT INTO user_suggestion_tickets (userId, suggestion)
                VALUES (?, ?)
                """,
                (interaction.user.id, suggestion)
            )
            await db.commit()
            
            # Get the ticket id from the database
            ticket_id = await db.execute_fetchall("SELECT * FROM user_suggestion_tickets")
            ticket_id = ticket_id[-1][0]  # last ticket -> first column

        # Create a channel for the ticket
        channel = await self.create_ticket_channel(prefix='suggestion', ticket_id=ticket_id)

        # Create an embed for the ticket
        embed = discord.Embed(colour=interaction.user.colour, title=f'Suggestion Ticket #{ticket_id}')
        embed.add_field(name='Suggestion From', value=interaction.user.mention, inline=False)
        embed.add_field(name='Suggestion/Feature Request', value=suggestion, inline=False)

        # Send the embed to the new channel and inform the user that the ticket
        # has been submitted and processed.
        await channel.send(embed=embed)
        await interaction.followup.send(TICKET_SUBMITTED, ephemeral=True)

    @group.command(name='report')
    async def create_report_ticket(self, interaction: discord.Interaction, accusing:discord.Member, *, reason: str):
        """
        Report a user for misbehaviour or bullying
        """

        # Shotcuts for replying to the user
        respond = interaction.response.send_message
        followup = interaction.followup.send

        # Prevent troll users from reporting themselves
        if accusing == interaction.user:
            await respond('You cannot report yourself\n  ╰(ಠ ͟ʖ ಠ)╯', ephemeral=True)
            return

        # Show that the bot is thinking to prevent the interaction timing out
        await interaction.response.defer(ephemeral=True)

        # Write the ticket to the database
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(
                """
                INSERT INTO user_report_tickets (userId, offenderUserId, messageContent) 
                VALUES (?, ?, ?)
                """,
                (interaction.user.id, accusing.id, reason)
            )
            await db.commit()

            # Get the ticket id from the database
            ticket_id = await db.execute_fetchall("SELECT * FROM user_report_tickets")
            ticket_id = ticket_id[-1][0]  # last ticket -> first column

        # Create a channel for the ticket
        channel = await self.create_ticket_channel(prefix='report', ticket_id=ticket_id)

        # Create an embed for the ticket
        embed = discord.Embed(colour=interaction.user.colour, title=f'Report Ticket #{ticket_id}')
        embed.add_field(name='Report By:', value=interaction.user.mention, inline=False)
        embed.add_field(name='Accusing:', value=accusing.mention, inline=False)
        embed.add_field(name='Reason Given:', value=reason, inline=False)

        # Send the embed to the new channel and inform the user that the ticket
        # has been submitted and processed.
        await channel.send(embed=embed)
        await followup(TICKET_SUBMITTED, ephemeral=True)
        
        
    


async def setup(bot):
    """
    Setup function.
    Required for all cog files.
    Used by the bot to load this cog.
    """

    cog = Tickets(bot)
    await bot.add_cog(cog, guilds=(bot.main_guild,))
