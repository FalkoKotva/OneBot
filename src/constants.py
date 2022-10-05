"""
This file contains all the constants used in the bot.
"""

from enum import Enum, auto


# Server Constants
GUILD_ID = 1017473530151059548
TICKETS_CATEGORY_ID = 1017881107930304533
ADMIN_ROLE_ID = 1017486791395250196
MODERATOR_ROLE_ID = None  # TODO

# Server Channels
class Channels:
    WELCOME = 1017473530620805193
    RULES = 1017501673360478272
    ROLES = 1017473632819224577
    MENTAL_HEALTH = 1019971468769120296
    FIND_HELP = 1019974533794496532
    ASK_TICKETS = 1018955680901775402
    ASK_HELP = 1017505667801682063
    LOGS = 1027136118484906045


# Other constants
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
