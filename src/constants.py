"""
This file contains all the constants used in the bot.
"""

from enum import Enum, auto


# Server Constants
GUILD_ID = 1017473530151059548
TICKETS_CATEGORY_ID = 1017881107930304533

TICKET_SUBMITTED_MSG = 'Your ticket has been submitted and processed.'
DATABASE = 'db.sqlite3'

# Ticket Enums

class TicketType(Enum):
    SUGGESTION = auto()
    REPORT = auto()
