import sqlite3
import time
from langchain_core.tools import tool
from config.settings import settings

def initTodoList():
    conn = sqlite3.connect(settings.todoListPath)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS todoList (
    id integer primary key not null,
    title text not null,
    description text null,
    status text not null default 'pending',
    createdAtUTCDay INT not null,
    dueAtUTCDay INT null);
    ''')
    conn.commit()
    conn.close()

def getCurrentUTCDay():
    return time.time() // (24 * 60 * 60)
def getDueDateUTCDay(dueDate):
    return dueDate.timestamp() // (24 * 60 * 60)

@tool
def addTodo(title, dueDate, description=None):
    '''
    Adds a new task that needs to be done into the todo list database.
    If the task is added successfully, respond with "Task added successfully."
    If the task is not added successfully, respond with "Sorry, right now I cannot add the task to the todo list."
    Args:
        title (str): The title or the name of the task
        description (str): The description of the task, which is optional.
        dueDate (str): The due date of the task in the format of 'YYYY-MM-DD'.
    Returns:
        return nothing if the task is added successfully, otherwise return nothing.
    '''
    if description is None:
        modifiedDescription = 'null'
    else:
        modifiedDescription = description
    conn = sqlite3.connect(settings.todoListPath)
    cur = conn.cursor()
    cur.execute(f'''INSERT INTO todolist (title, description, status, createdAtUTCDay, dueAtUTCDay)
    VALUES ('{title}', '{modifiedDescription}', 'pending', '{getCurrentUTCDay()}', '{getDueDateUTCDay(dueDate)}')
    ''')