"""
Use this file to setup the database
"""

import sqlite3

from constants import DATABASE


def setup():
    """
    Setup the database file and tables
    """

    db = sqlite3.connect(DATABASE)
    cur = db.cursor()

    # Create the table for report tickets
    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_report_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            accused_user_id INTEGER NOT NULL,
            channel_id INTEGER,
            reason_msg TEXT NOT NULL
        )"""
    )

    # Create the table for suggestion tickets
    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_suggestion_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            channel_id INTEGER,
            suggestion_msg TEXT NOT NULL
            )
        """
    )

    db.commit()
    db.close()

if __name__ == '__main__':
    setup()