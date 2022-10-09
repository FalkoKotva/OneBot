"""Database interaction functions"""

import logging
from os.path import isfile
from sqlite3 import connect
from apscheduler.triggers.cron import CronTrigger

DB_PATH = './data/db/db.sqlite3'
BUILD_PATH = './data/db/build.sql'

log = logging.getLogger(__name__)

# Connect to the database
conn = connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

def with_commit(func):
    """Wrapper to commit changes to the database"""

    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner

@with_commit
def build():
    """Build the database from the build script"""

    if isfile(BUILD_PATH):
        scriptexec(BUILD_PATH)
        return

    raise ValueError('Build script not found')

def commit():
    """Commit changes to the database"""

    conn.commit()

def autosave(sched):
    """"""

    sched.add_job(commit, CronTrigger(second=0))

def close():
    """Close the database connection"""

    conn.close()

def field(cmd, *vals):
    """Return a single field"""

    cur.execute(cmd, tuple(vals))

    # If row exists, return the first row
    if (fetch := cur.fetchone()) is not None:
        return fetch[0]

def record(cmd, *vals):
    """Return a single record"""

    cur.execute(cmd, tuple(vals))
    return cur.fetchone()

def records(cmd, *vals):
    """Return all records"""

    cur.execute(cmd, tuple(vals))
    return cur.fetchall()

def column(cmd, *vals):
    """Return a single column"""

    cur.execute(cmd, tuple(vals))
    return [item[0] for item in cur.fetchall()]

def execute(cmd, *vals):
    """Execute a command"""

    cur.execute(cmd, tuple(vals))

def multiexec(cmd, valset):
    """Execute multiple commands"""

    cur.executemany(cmd, valset)

def scriptexec(path):
    """Execute a script"""

    with open(path, 'r', encoding='utf-8') as script:
        cur.executescript(script.read())