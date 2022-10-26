CREATE TABLE IF NOT EXISTS user_birthdays (
    user_id INTEGER PRIMARY KEY,
    birthday TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS guilds (
    guild_id INTEGER PRIMARY KEY,
    prefix TEXT NOT NULL DEFAULT '!'
);

CREATE TABLE IF NOT EXISTS member_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    experience INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEy (guild_id) REFERENCES guilds(guild_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS guild_mutes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    reason TEXT,
    end_datetime TEXT NOT NULL,
    FOREIGN KEY (guild_id) REFERENCES guilds(guild_id) ON DELETE CASCADE
);

-- Channel keys are used by modules in the bot to identify channels
CREATE TABLE IF NOT EXISTS guild_channel_purposes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Add the default channel keys
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('general');
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('announcements');
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('members_say_welcome');
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('members_say_goodbye');
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('bot_logs');
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('bot_commands');

CREATE TABLE IF NOT EXISTS guild_channels (
    channel_id INTEGER PRIMARY KEY,
    guild_id INTEGER NOT NULL,
    purpose_id INTEGER NOT NULL,
    FOREIGN KEY (guild_id) REFERENCES guilds (guild_id) ON DELETE CASCADE,
    FOREIGN KEY (purpose_id) REFERENCES guild_channel_purposes(id) ON DELETE CASCADE
);

-- 
CREATE TABLE IF NOT EXISTS guild_role_purposes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

INSERT OR IGNORE INTO guild_role_purposes (name) VALUES ('member');
INSERT OR IGNORE INTO guild_role_purposes (name) VALUES ('admin');
INSERT OR IGNORE INTO guild_role_purposes (name) VALUES ('mod');
INSERT OR IGNORE INTO guild_role_purposes (name) VALUES ('muted');
INSERT OR IGNORE INTO guild_role_purposes (name) VALUES ('verified');
INSERT OR IGNORE INTO guild_role_purposes (name) VALUES ('birthday');

CREATE TABLE IF NOT EXISTS guild_roles (
    role_id INTEGER PRIMARY KEY,
    guild_id INTEGER NOT NULL,
    purpose_id INTEGER NOT NULL,
    FOREIGN KEY (guild_id) REFERENCES guilds (guild_id) ON DELETE CASCADE,
    FOREIGN KEY (purpose_id) REFERENCES guild_role_purposes(id) ON DELETE CASCADE
);

