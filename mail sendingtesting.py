import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
load_dotenv()
email_user = os.getenv("EMAIL_USER")
email_pass = os.getenv("EMAIL_PASS")
smtp_server = os.getenv("SMTP_SERVER")
imap_server = os.getenv("IMAP_SERVER")


class emailTool:
    def __init__(self,emailAddress,emailPassword,smtpServer,imapServer):
        self.emailAddress = emailAddress
        self.emailPassword = emailPassword
        self.smtpServer = smtpServer
        self.imapServer = imapServer
        self.stmpOBJ = smtplib.SMTP_SSL(self.smtpServer, 465)
    def sendEmail(self,recipientEmail,subject,body):
        self.stmpOBJ.login(self.emailAddress, self.emailPassword)
        MSG = MIMEText(body)
        MSG['Subject'] = subject
        MSG['From'] = self.emailAddress
        MSG['To'] = recipientEmail
        self.stmpOBJ.send_message(MSG)
        self.stmpOBJ.quit()
if __name__ == "__main__":
    email_tool = emailTool(email_user,email_pass,smtp_server,imap_server)
    email_tool.sendEmail("stephen_xu2005@126.com", "Test Subject", "Test Body")
    print("Email sent successfully.")
