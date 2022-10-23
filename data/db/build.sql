CREATE TABLE IF NOT EXISTS user_birthdays (
    user_id INTEGER PRIMARY KEY,
    birthday TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS member_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    experience INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS guild_channels (
    channel_id INTEGER PRIMARY KEY,
    guild_id INTEGER NOT NULL,
    purpose_id INTEGER NOT NULL,
    FOREIGN KEY (purpose_id) REFERENCES channel_purposes(id)
);

-- Channel keys are used by modules in the bot to identify channels
CREATE TABLE IF NOT EXISTS guild_channel_purposes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Add the default channel keys
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('general');
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('welcome');
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('goodbye');
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('announcements');
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('logs');
INSERT OR IGNORE INTO guild_channel_purposes (name) VALUES ('bots');


CREATE TABLE IF NOT EXISTS guild_roles (
    role_id INTEGER PRIMARY KEY,
    guild_id INTEGER NOT NULL,
    purpose_id INTEGER NOT NULL,
    FOREIGN KEY (purpose_id) REFERENCES role_purposes(id)
);

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
