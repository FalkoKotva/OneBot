"""
This file contains all the constants used in the bot.
"""

from enum import Enum, auto


# Server Constants
GUILD_ID = 1017473530151059548
TICKETS_CATEGORY_ID = 1017881107930304533
ADMIN_ROLE_ID = 1017486791395250196
MODERATOR_ROLE_ID = None  # TODO

# Other constants
TICKET_SUBMITTED_MSG = 'Your ticket has been submitted and processed.'
DATABASE = 'db.sqlite3'
LOGS = 'logs/'
LOG_FILENAME_FORMAT_PREFIX = '%Y-%m-%d %H-%M-%S'
MAX_LOGFILE_AGE_DAYS = 7

# Ticket Enums
class TicketType(Enum):
    SUGGESTION = auto()
    REPORT = auto()
