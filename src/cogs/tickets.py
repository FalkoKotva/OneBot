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
    TICKET_SUBMITTED_MSG,
    TICKETS_CATEGORY_ID,
    TicketType
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
    
    def create_ticket_embed(self, ticket_type:TicketType, ticket_id:int, *args):
        """
        Creates and returns a discord Embed for use in tickets.
        """

        embed = discord.Embed(colour=args[0].colour, title=f"{ticket_type.name.title()} Ticket #{ticket_id}")

        if ticket_type == ticket_type.REPORT:
            embed.add_field(name="Accused", value=args[0].mention, inline=False)
            embed.add_field(name="Reason Given", value=args[1], inline=False)

        else:
            embed.add_field(name="Suggestion From", value=args[0].mention, inline=False)
            embed.add_field(name="Suggestion/Feature Request", value=args[1], inline=False)

        return embed

    async def create_ticket(self, interaction:discord.Interaction, ticket_type:TicketType, *args):
        """
        Create a ticket.
        """

        # Shortcuts for replying to the user
        respond = interaction.response.send_message
        followup = interaction.followup.send
        
        get_id_sql = "SELECT ticketId FROM {0} ORDER BY ticketId DESC LIMIT 1"

        normalized_sql_values = []
        for arg in args:
            if isinstance(arg, discord.Member):
                normalized_sql_values.append(arg.id)
                continue

            normalized_sql_values.append(arg)

        if ticket_type == TicketType.REPORT:
            
            # Prevent troll users from creating tickets that report themselves
            if args[1] == interaction.user:
                await respond('You cannot report yourself\n  ╰(ಠ ͟ʖ ಠ)╯', ephemeral=True)
                return

            # Code to create a report ticket in the database
            ticket_sql = """
                INSERT INTO user_report_tickets (userId, offenderUserId, messageContent) 
                VALUES (?, ?, ?)
                """
            get_id_sql = get_id_sql.format('user_report_tickets')
        else:

            # Code to create a suggestion ticket in the database
            ticket_sql = """
                INSERT INTO user_suggestion_tickets (userId, suggestion)
                VALUES (?, ?)
                """
            get_id_sql = get_id_sql.format('user_suggestion_tickets')

        # Show that the bot is thinking to prevent the interaction timing out
        await interaction.response.defer(ephemeral=True)

        # Write the ticket to the database
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(ticket_sql, normalized_sql_values)
            await db.commit()
            ticket_id = await db.execute_fetchall(get_id_sql)
            ticket_id = ticket_id[0][0]  # get value from [(int,)]

        # Create a channel for the new ticket
        channel = await self.create_ticket_channel(
            prefix=ticket_type.name.lower(),
            ticket_id=ticket_id
        )

        # Create an embed for the ticket
        embed = self.create_ticket_embed(
            ticket_type,
            ticket_id,
            *args
        )
        await channel.send(embed=embed)

        # We have done our work here, time to let the user know that.
        await followup(TICKET_SUBMITTED_MSG, ephemeral=True)
        
        
    
    @group.command(name='suggestion')
    async def create_suggestion_ticket(self, interaction:discord.Interaction, *, suggestion:str):
        """
        Suggest a feature for the server
        """
        await self.create_ticket(interaction, TicketType.SUGGESTION, interaction.user, suggestion)
        return
        
        # Show that the bot is thinking to prevent the interaction timing out
        await interaction.response.defer(ephemeral=True)

        # Write the ticket to the database
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

        
        embed = discord.Embed(colour=interaction.user.colour, title=f'Suggestion Ticket #{ticket_id}')
        # embed.add_field(name='Suggestion From', value=interaction.user.mention, inline=False)
        # embed.add_field(name='Suggestion/Feature Request', value=suggestion, inline=False)

        # Send the embed to the new channel and inform the user that the ticket
        # has been submitted and processed.
        await channel.send(embed=embed)
        await interaction.followup.send(TICKET_SUBMITTED_MSG, ephemeral=True)

    @group.command(name='report')
    async def create_report_ticket(self, interaction: discord.Interaction, accusing:discord.Member, *, reason: str):
        """
        Report a user for misbehaviour or bullying
        """
        await self.create_ticket(interaction, TicketType.REPORT, interaction.user, accusing, reason)
        return

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
        await followup(TICKET_SUBMITTED_MSG, ephemeral=True)
        
        
    


async def setup(bot):
    """
    Setup function.
    Required for all cog files.
    Used by the bot to load this cog.
    """

    cog = Tickets(bot)
    await bot.add_cog(cog, guilds=(bot.main_guild,))
