"""
This file contains all the constants used in the bot.
"""

from enum import Enum, auto


TICKET_SUBMITTED_MSG = 'Your ticket has been submitted and processed.'
DATABASE = 'db.sqlite3'
LOGS = 'logs/'
LOG_FILENAME_FORMAT_PREFIX = '%Y-%m-%d %H-%M-%S'
MAX_LOGFILE_AGE_DAYS = 7
ACTIVITY_MSG = 'I am up and running!'

# Member Profile Card Constants
AVATAR_SIZE = (150, 150)
BANNER_SIZE = (401, 116)

# Ticket Enums
class TicketType(Enum):
    SUGGESTION = auto()
    REPORT = auto()
