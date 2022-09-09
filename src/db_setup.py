"""
Use this file to setup the database
"""

import sqlite3
from constants import DATABASE


def main():
    
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    
    # Create the table for report tickets
    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_report_tickets (
            ticketId INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER NOT NULL,
            offenderUserId INTEGER NOT NULL,
            messageContent TEXT NOT NULL
        )"""
    )

    # Create the table for suggestion tickets
    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_suggestion_tickets (
            ticketId INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER NOT NULL,
            suggestion TEXT NOT NULL
            )
        """
    )
    
    db.commit()
    db.close()
    

if __name__ == '__main__':
    main()