import sqlite3
import time
from langchain_core.tools import tool
from config.settings import settings
from .timeTools import convertISOToUTCEpoch, getUTCNow



def initTodoList():
    conn = sqlite3.connect(settings.todoListPath)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS todoList (
    id integer primary key not null,
    title text not null,
    description text null,
    status text not null default 'pending',
    createdAtUTC INT not null,
    dueAtUTC INT null);
    ''')
    conn.commit()
    conn.close()

def getCurrentUTCEpoch():
    return time.time()
def getDueDateUTCEpoch(dueDate):
    return convertISOToUTCEpoch(dueDate)

@tool
def addTodo(title, dueDate, description=None):
    '''
    Insert a new pending task into the todo list database.

    Input rules for `dueDate`:
    - If `dueDate` is already a valid ISO 8601 datetime string (e.g. "2024-01-01T12:00:00Z"
      or with an offset like "+08:00"), pass it through unchanged.
    - If `dueDate` is a datetime string without timezone (e.g. "2024-01-01 12:00:00"),
      convert it to ISO 8601 and assume UTC (append "Z").
    - If `dueDate` is relative or vague (e.g. "tomorrow", "next week", "in three weeks"),
      you MUST call `getUTCNow()` first to obtain the current UTC time, then compute the
      resulting absolute due datetime, and pass the final result in ISO 8601 format.

    Do NOT guess or fabricate timestamps.

    Args:
        title (str): Short task title.
        dueDate (str): Due datetime. Prefer ISO 8601. If not ISO 8601, normalize to ISO 8601.
        description (str, optional): Longer task description.

    Returns:
        str: "Task added successfully." if the insert succeeds.

    Raises:
        Exception: Propagates database or parsing errors (caller may catch and respond).
    '''
    conn = sqlite3.connect(settings.todoListPath)
    cur = conn.cursor()
    cur.execute('''INSERT INTO todoList (title, description, status, createdAtUTC, dueAtUTC)
    VALUES (?, ?, 'pending', ?, ?)
    ''',(title, description, getCurrentUTCEpoch(), getDueDateUTCEpoch(dueDate)))
    conn.commit()
    conn.close()
    return "Task added successfully."
    