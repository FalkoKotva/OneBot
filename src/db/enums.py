"""Database enums"""

from enum import Enum

from db import db


# Settings
_settings_data = db.records("SELECT id, safe_name FROM settings")
_settings_map = {name: _id for _id, name in _settings_data}
UserSettingsNames = Enum("UserSettingsNames", _settings_map)

# Channel Purposes
_channel_purposes_data = db.records("SELECT * FROM guild_channel_purposes")
_channel_purposes_map = {name: _id for _id, name in _channel_purposes_data}
ChannelPurposes = Enum("ChannelPurposes", _channel_purposes_map)

_role_purposes_data = db.records("SELECT * FROM guild_role_purposes")
_role_purposes_map = {name: _id for _id, name in _role_purposes_data}
RolePurposes = Enum("RolePurposes", _role_purposes_map)