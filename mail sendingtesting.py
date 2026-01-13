import smtplib
import imaplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
load_dotenv()
email_user = os.getenv("OTS_EMAIL_USER")
email_pass = os.getenv("OTS_EMAIL_PASS")
smtp_server = os.getenv("OTS_SMTP_SERVER")
imap_server = os.getenv("OTS_IMAP_SERVER")


class emailTool:
    def __init__(self,emailAddress,emailPassword,smtpServer,imapServer):
        self.emailAddress = emailAddress
        self.emailPassword = emailPassword
        self.smtpServer = smtpServer
        self.imapServer = imapServer
        self.stmpOBJ = smtplib.SMTP_SSL(self.smtpServer, 465)
        self.imapOBJ = imaplib.IMAP4_SSL(self.imapServer)
    def sendEmail(self,recipientEmail,subject,body):
        self.stmpOBJ.login(self.emailAddress, self.emailPassword)
        MSG = MIMEText(body)
        MSG['Subject'] = subject
        MSG['From'] = self.emailAddress
        MSG['To'] = recipientEmail
        self.stmpOBJ.send_message(MSG)
        self.stmpOBJ.quit()
    def getEmail(self):
        self.imapOBJ.login(self.emailAddress, self.emailPassword)
        s,data = self.imapOBJ.select("INBOX")
        if s == "OK":
            print(data)
        else:
            print("Failed to select INBOX")
            return None
        status, email_ids = self.imapOBJ.search(None, "ALL")
        print(status)
        print(email_ids)
        return email_ids
if __name__ == "__main__":
    email_tool = emailTool(email_user,email_pass,smtp_server,imap_server)
    print(email_tool.getEmail())
