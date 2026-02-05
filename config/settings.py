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
        self.modelName = "gpt-oss:120b-cloud"#'qwen3:8b'
        self.toolModelName = 'qwen3:0.6b'
        self.apiKey = os.getenv('OPENAI_API_KEY')
        self.dataBasePath = baseDir / 'data' / 'CorqueDB.db'
        self.localTimeZone = str(get_localzone())
        self.numOfThreads = os.cpu_count()
        self.tavilyApiKey = os.getenv('TAVILY_API_KEY')

settings = Settings()