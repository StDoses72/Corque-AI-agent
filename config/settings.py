from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from tzlocal import get_localzone
import os

baseDir = Path(__file__).resolve().parent.parent

load_dotenv(find_dotenv())

class Settings:
    def __init__(self):
        self.emailUser = os.getenv('OTS_EMAIL_USER')
        self.emailPass = os.getenv('OTS_EMAIL_PASS')
        self.smtpServer = os.getenv('OTS_SMTP_SERVER')
        self.imapServer = os.getenv('OTS_IMAP_SERVER')
        self.modelName = 'llama3.1:8b'
        self.todoListPath = baseDir / 'data' / 'todoList.db'
        self.localTimeZone = str(get_localzone())

settings = Settings()