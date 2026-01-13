import sqlite3
from langchain_core.tools import tool
from config.settings import settings

def initTodoList():
    conn = sqlite3.connect(settings.todoListPath)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS todoList (
    id integer primary key not null,
    title text not null,
    description text not null,
    dueDate text not null,
    status text not null,
    createdAt text not null);
    ''')
    conn.commit()
    conn.close()