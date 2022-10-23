"""This file contains all the constants used in the bot."""

from enum import Enum

from easy_pil import Font

from db import db

# Bot constants
ACTIVITY_MSG = 'I am up and running!'
DATE_FORMAT = '%d/%m/%Y'

# Command constants
BDAY_HELP_MSG = 'Use `/birthday help` for more info'

# MSGS
BAD_TOKEN = 'You have passed an improper or invalid token! Shutting down...'
NO_TOKEN = 'TOKEN file not found in project root! Shutting down...'
NO_CONFIG = 'CRITICAL ERROR: config file is missing! Shutting down...'

# Logging constants
LOGS = 'logs/'
LOG_FILENAME_FORMAT_PREFIX = '%Y-%m-%d %H-%M-%S'
MAX_LOGFILE_AGE_DAYS = 7

# Levelboard constants
# colours
BLACK = "#0F0F0F"
WHITE = "#F9F9F9"
DARK_GREY = "#2F2F2F"
LIGHT_GREY = "#9F9F9F"
#fonts
POPPINS = Font.poppins(size=70)
POPPINS_SMALL = Font.poppins(size=50)

# Channel Purposes
_channel_purposes_data = db.records("SELECT * FROM guild_channel_purposes")
_channel_purposes_map = {name: _id for _id, name in _channel_purposes_data}
ChannelPurposes = Enum("ChannelPurposes", _channel_purposes_map)

_role_purposes_data = db.records("SELECT * FROM guild_role_purposes")
_role_purposes_map = {name: _id for _id, name in _role_purposes_data}
RolePurposes = Enum("RolePurposes", _role_purposes_map)
