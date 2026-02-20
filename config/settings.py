from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from tzlocal import get_localzone
import os

baseDir = Path(__file__).resolve().parent.parent

load_dotenv(find_dotenv())

class Settings:
    def __init__(self):
        self.emailUser = os.getenv('EMAIL_USER')
        self.emailPass = os.getenv('EMAIL_PASS')
        self.smtpServer = os.getenv('SMTP_SERVER')
        self.imapServer = os.getenv('IMAP_SERVER')
        self.modelName = "glm-4.7-flash"#'qwen3:8b'
        self.codingModelName = 'qwen3-coder-next:q4_K_M'
        self.apiKey = os.getenv('DEDALUS_API_KEY')
        self.dataBasePath = baseDir / 'data' / 'CorqueDB.db'
        self.localTimeZone = str(get_localzone())
        self.senderName = os.getenv('SENDER_NAME') or "Corque"
        self.userName = os.getenv('USER_NAME') or "Corque"
        self.region = os.getenv('REGION') or ''
        self.numOfThreads = os.cpu_count()
        self.tavilyApiKey = os.getenv('TAVILY_API_KEY')
        self.workspaceDir = baseDir / 'workspace'

    def apply_overrides(self, overrides: dict) -> None:
        if not overrides:
            return
        if overrides.get('model'):
            self.modelName = overrides['model']
        if overrides.get('timezone'):
            self.localTimeZone = overrides['timezone']
        if overrides.get('senderName') is not None:
            self.senderName = overrides['senderName']
        if overrides.get('name') is not None:
            self.userName = overrides['name']
        if overrides.get('region') is not None:
            self.region = overrides['region']

settings = Settings()