from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    def __init__(self):
        self.emailUser = os.getenv('OTS_EMAIL_USER')
        self.emailPass = os.getenv('OTS_EMAIL_PASS')
        self.smtpServer = os.getenv('OTS_SMTP_SERVER')
        self.imapServer = os.getenv('OTS_IMAP_SERVER')
        self.modelName = 'qwen3:14b'

settings = Settings()