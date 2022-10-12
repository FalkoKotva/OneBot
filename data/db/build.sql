CREATE TABLE IF NOT EXISTS user_birthdays (
    user_id INTEGER PRIMARY KEY,
    birthday TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    extra_info TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_report_tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    accused_user_id INTEGER NOT NULL,
    channel_id INTEGER,
    reason_msg TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_suggestion_tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    channel_id INTEGER,
    suggestion_msg TEXT NOT NULL
);