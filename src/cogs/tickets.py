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

    # Ticket command group.
    group = app_commands.Group(
        name='ticket',
        description='Open tickets here...',
        guild_ids=(GUILD_ID,)
    )

    async def create_ticket_channel(
        self, prefix:str, ticket_id:int
        ) -> discord.TextChannel:
        """
        Creates and returns a discord TextChannel object to store a
        new ticket.
        """

        # The guild and category where the new channel will be created
        guild: discord.Guild = self.bot.get_guild(GUILD_ID)
        category: discord.CategoryChannel = discord.Object(
            id=TICKETS_CATEGORY_ID
        )

        # Return the newly created ticket channel
        return await guild.create_text_channel(
            name=f"{prefix}-ticket-{ticket_id}",
            category=category
        )
    
    def create_ticket_embed(
        self, ticket_type:TicketType, ticket_id:int, *args
        ):
        """
        Creates and returns a discord Embed for use in tickets.
        """

        # The embed that will be returned
        embed = discord.Embed(
            colour=args[0].colour,
            title=f"{ticket_type.name.title()} Ticket #{ticket_id}"
        )
        
        # Add the ticket details to the embed via fields
        if ticket_type == ticket_type.REPORT:
            embed.add_field(name="Accuser", value=args[0].mention, inline=False)
            embed.add_field(name="Accusing", value=args[1].mention, inline=False)
            embed.add_field(name="Reason Given", value=args[2], inline=False)
        else:
            embed.add_field(name="Suggestion From", value=args[0].mention, inline=False)
            embed.add_field(name="Suggestion/Feature Request", value=args[1], inline=False)

        return embed

    async def create_ticket(
        self,
        interaction:discord.Interaction,
        ticket_type:TicketType,
        *args
        ):
        """
        Create a new ticket. This will create a new channel and
        embed for the ticket.
        """

        # Show that the bot is thinking to prevent the interaction timing out
        await interaction.response.defer(ephemeral=True)

        # Shorthands for replying to the user
        followup = interaction.followup.send

        # This sql query will get the next ticket id
        get_id_sql = "SELECT ticket_id FROM {0} ORDER BY ticket_id " \
                     "DESC LIMIT 1"

        # Normalize the data to be inserted into the database
        normalized_sql_values = []
        for arg in args:
            
            # If the arg is a discord.Member object, get the id instead
            if isinstance(arg, discord.Member):
                normalized_sql_values.append(arg.id)
                continue

            # Otherwise just append the value
            normalized_sql_values.append(arg)

        # Determine what sql query to use based on the ticket type
        if ticket_type == TicketType.REPORT:
            
            # Prevent troll users from creating tickets that report themselves
            if args[1] == interaction.user:
                await followup(
                    'You cannot report yourself\n  ╰(ಠ ͟ʖ ಠ)╯',
                    ephemeral=True
                )
                return

            table = 'user_report_tickets'
            values = '(user_id, accused_user_id, channel_id, reason_msg) VALUES (?, ?, NULL, ?)'
        elif ticket_type == TicketType.SUGGESTION:
            table = 'user_suggestion_tickets'
            values = '(user_id, channel_id, suggestion_msg) VALUES (?, NULL, ?)'

        
        ticket_query = f'INSERT INTO {table} {values}'
        get_id_sql = get_id_sql.format(table)

        print('writing ticket to db')
        # Write the ticket to the database
        async with aiosqlite.connect(DATABASE) as db:
            print(ticket_query)
            await db.execute(ticket_query, normalized_sql_values)
            await db.commit()
            
            print('ticket written, getting id')
            # Get the ticket id of the newly created ticket
            ticket_id = await db.execute_fetchall(get_id_sql)
            ticket_id = ticket_id[0][0]  # get value from [(int,)])

        print('id obtained, creating channel')
        # Create a channel for the new ticket to be discussed in
        channel = await self.create_ticket_channel(
            prefix=ticket_type.name.lower(),
            ticket_id=ticket_id
        )

        # Store the channel id in the database with the ticket
        channel_query = f"UPDATE {table} SET channel_id = ? WHERE ticket_id = ?"
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(channel_query, (channel.id, ticket_id))
            await db.commit()

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
    @app_commands.describe(suggestion='Your suggestion or feature request')
    async def create_suggestion_ticket(
        self,
        interaction:discord.Interaction,
        *, suggestion:str
    ):
        """
        Suggest a feature for the server
        """
        await self.create_ticket(
            interaction, TicketType.SUGGESTION,
            interaction.user,
            suggestion
        )

    @group.command(name='report')
    @app_commands.describe(
        accusing='The user you are accusing',
        reason='The reason you are accusing them'
    )
    async def create_report_ticket(
        self,
        interaction: discord.Interaction,
        accusing:discord.Member,
        *, reason: str
    ):
        """
        Report a user for misbehaviour or bullying
        """
        await self.create_ticket(
            interaction, TicketType.REPORT,
            interaction.user,
            accusing,
            reason
        )
    
    # @group.command(name='close')
    # async def close_ticket(
    #     self,
    #     interaction:discord.Interaction,
    #     ticket_type:TicketType,
    #     ticket_id:int
    # ):
    #     """
    #     Close a ticket (admin/mod only)
    #     """

    #     # Shorthand for replying to the user
    #     send = interaction.response.send_message

    #     # Find the correct table to use based on the ticket type
    #     if ticket_type == TicketType.REPORT:
    #         table = 'user_report_tickets'
    #     elif ticket_type == TicketType.SUGGESTION:
    #         table = 'user_suggestion_tickets'
    #     else:
    #         raise ValueError('Invalid ticket type')  # This should never happen

    #     query = f'FROM {table} WHERE ticket_id=?'

    #     # Check that the ticket exists
    #     async with aiosqlite.connect(DATABASE) as db:
    #         try:
    #             result = await db.execute_fetchall(
    #                 'SELECT ticket_id ' + query,
    #                 (ticket_id,)
    #             )
    #             result[0][0]  # raises IndexError if ticket doesn't exist
    #         except IndexError:
    #             await send(
    #                 f'There are no {ticket_type.name.lower()} ' \
    #                 f'tickets with the id: {ticket_id}',
    #                 ephemeral=True
    #             )
    #             return        

    #     # Delete the ticket from the database
    #     async with aiosqlite.connect(DATABASE) as db:
    #         await db.execute('DELETE ' + query,(ticket_id,))
    #         await db.commit()

    #     # TODO: Delete the ticket channel

    #     await send('Ticket closed', ephemeral=True)


async def setup(bot):
    """
    Setup function.
    Required for all cog files.
    Used by the bot to load this cog.
    """

    cog = Tickets(bot)
    await bot.add_cog(cog, guilds=(bot.main_guild,))
