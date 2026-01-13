from pathlib import Path
from dotenv import load_dotenv
import os

baseDir = Path(__file__).resolve().parent.parent

load_dotenv()

class Settings:
    def __init__(self):
        self.emailUser = os.getenv('OTS_EMAIL_USER')
        self.emailPass = os.getenv('OTS_EMAIL_PASS')
        self.smtpServer = os.getenv('OTS_SMTP_SERVER')
        self.imapServer = os.getenv('OTS_IMAP_SERVER')
        self.modelName = 'qwen3:8b'
        self.todoListPath = baseDir / 'data' / 'todoList.db'

settings = Settings()