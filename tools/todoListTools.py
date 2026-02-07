import sqlite3
import time
from langchain_core.tools import tool
from config.settings import settings
from .timeTools import convertISOToUTCEpoch, getUTCNow, convertUTCEpochToISO, convertUTCToLocal



def initTodoList():
    conn = sqlite3.connect(settings.dataBasePath)
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
def addTodo(title, dueDate, description=None) -> str:
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
    conn = sqlite3.connect(settings.dataBasePath)
    cur = conn.cursor()
    cur.execute('''INSERT INTO todoList (title, description, status, createdAtUTC, dueAtUTC)
    VALUES (?, ?, 'pending', ?, ?)
    ''',(title, description, getCurrentUTCEpoch(), getDueDateUTCEpoch(dueDate)))
    conn.commit()
    conn.close()
    return "Task added successfully."

@tool
def getTodoListinDaysFromNow(days) -> list:
    '''
    Get the todo list with the due date within the days from now.
    The due date is in UTC time.
    You can use `convertUTCEpochToISO(epochSeconds)` to convert the due date in UTC epoch seconds to ISO time string.
    You can use `convertUTCToLocal(isoTimeString)` to convert the due date in ISO time string to local time string.
    The local time is in the system's local timezone.
    The local timezone is the timezone of the system.
    Args:
        days (int): The number of days from now.
    Returns:
        list: A list of todo list with the due date in local time string.
    '''
    conn = sqlite3.connect(settings.dataBasePath)
    cur = conn.cursor()
    currentUTCEpoch = getCurrentUTCEpoch()
    cur.execute('''SELECT * FROM todoList 
    WHERE dueAtUTC IS NOT NULL AND dueAtUTC-?<=?*24*60*60 AND dueAtUTC>=? 
    ORDER BY dueAtUTC ASC''',(currentUTCEpoch,days,currentUTCEpoch))
    todoList = cur.fetchall()
    if len(todoList) == 0:
        conn.close()
        return "No todo list found."
    else:
        conn.close()
        localTodoList = []
        for todo in todoList:
            localTodoList.append({'id': todo[0], 
                                'title': todo[1], 
                                'description': todo[2],
                                'status': todo[3], 
                                'dueAtLocal': convertUTCToLocal(convertUTCEpochToISO(todo[5]), localTimeZone=settings.localTimeZone),
                                'createdAtLocal': convertUTCToLocal(convertUTCEpochToISO(todo[4]), localTimeZone=settings.localTimeZone),
                                'daysFromNow': (todo[5] - currentUTCEpoch) / (24 * 60 * 60)})
        return localTodoList

@tool
def getMostRecentTodo(numberOfTodos:int=2) -> list:
    '''
    Get the most recent todo list.
    The todo list is in the local time.
    The todo list is in the order of the due date.
    Args:
        numberOfTodos (int): The number of todos to get. Default is 2.
    Returns:
        list: A list of todo list with the due date in local time string.
    '''
    conn = sqlite3.connect(settings.dataBasePath)
    cur = conn.cursor()
    cur.execute('''SELECT * FROM todoList WHERE status = 'pending' ORDER BY dueAtUTC ASC LIMIT ?''',(numberOfTodos,))
    todoList = cur.fetchall()
    if len(todoList) == 0:
        conn.close()
        return "No todo list found."
    else:
        conn.close()
        localTodoList = []
        for todo in todoList:
            localTodoList.append({'id': todo[0],
                                'title': todo[1],
                                'description': todo[2],
                                'status': todo[3],
                                'dueAtLocal': convertUTCToLocal(convertUTCEpochToISO(todo[5]), localTimeZone=settings.localTimeZone),
                                'createdAtLocal': convertUTCToLocal(convertUTCEpochToISO(todo[4]), localTimeZone=settings.localTimeZone),
                                'daysFromNow': (todo[5] - getCurrentUTCEpoch()) / (24 * 60 * 60)})
        return localTodoList

@tool
def deleteTodo(todoId) -> str:
    '''
    Delete a todo from the todo list. Or mark a todo as completed.
    The todo is deleted from the todo list database.
    Args:
        todoId (int): The id of the todo to delete.
    Returns:
        str: A confirmation message if the todo is deleted successfully.
    '''
    conn = sqlite3.connect(settings.dataBasePath)
    cur = conn.cursor()
    cur.execute('''UPDATE todoList SET status = 'completed' WHERE id = ?''',(todoId,))
    print('Are your sure you want to delete the todo?')
    confirmation = input('Enter y to confirm, n to cancel: ')
    if confirmation in ('y', 'Y', 'yes', 'Yes', 'YES'):
        conn.commit()
        conn.close()
        return 'Todo deleted successfully.'
    else:
        conn.close()
        return 'Todo deletion cancelled.'

@tool
def changeTodoStatus(todoId, status) -> str:
    '''
    Change the status of a todo.
    The status is changed in the todo list database.
    Args:
        todoId (int): The id of the todo to change the status.
        status (str): The status to change to.
    Returns:
        str: A confirmation message if the status is changed successfully.
    '''
    print('Are your sure you want to change the status of the todo?')
    confirmation = input('Enter y to confirm, n to cancel: ')
    if confirmation in ('y', 'Y', 'yes', 'Yes', 'YES'):
        conn = sqlite3.connect(settings.dataBasePath)
        cur = conn.cursor()
        cur.execute('''UPDATE todolist SET status = ? WHERE id = ?''',(status,todoId))
        conn.commit()
        conn.close()
        return 'Todo status changed successfully.'
    else:
        return 'Todo status change cancelled.'