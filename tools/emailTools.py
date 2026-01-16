import smtplib
import imaplib
import time
from email.mime.text import MIMEText
from config.settings import settings
from langchain_core.tools import tool


@tool
def sendEmail(recipientEmail,subject,body,fromWho = 'XiangCheng Xu'):
    '''
    Sends an email to a specified recipient with a subject and message body. (向指定收件人发送电子邮件)
    If the email fails to send, return an error message.

    Args:
        recipientEmail (str): The complete email address of the recipient (e.g., 'example@gmail.com').
                            This argument is required.
        subject (str): The subject line of the email. It should be concise and relevant.
                    This argument is required.
        body (str): The main content or message of the email. 
                    This argument is required. A greeting may be included at the beginning of the body.
        fromWho (str): The name of the sender. Default is 'XiangCheng Xu'.

    Returns:
        str: A confirmation message if the email is sent successfully, or an error message otherwise.
    '''
    
    numOfRetries = 3
    for i in range(numOfRetries):
        try:
            fullBody = body.rstrip() + f"\n\nBest regards,\n{fromWho}"
            MSG = MIMEText(fullBody)
            MSG['Subject'] = subject
            MSG['From'] = settings.emailUser
            MSG['To'] = recipientEmail
            with smtplib.SMTP_SSL(settings.smtpServer, 465, local_hostname='localhost') as smtpOBJ:
                smtpOBJ.login(settings.emailUser, settings.emailPass)
                smtpOBJ.send_message(MSG)
            return 'Email sent successfully.'
        except Exception as e:
            if i<numOfRetries-1:
                print(f"Retrying to send email... Attempt {i+1}")
                time.sleep(0.5)
                continue
            print(f"Failed to send email after {numOfRetries} attempts.")
            return f'Error happens in sending email: {str(e)}'
@tool
def getEmail():
    '''
    Retrieves the email from the specified email address.
    If the email fails to retrieve, respond with "Sorry, I couldn't find the email at this time."
    '''
    imapOBJ = imaplib.IMAP4_SSL(settings.imapServer)
    imapOBJ.login(settings.emailUser, settings.emailPass)
    try:
        imapOBJ.select("INBOX")
        status, email_ids = imapOBJ.search(None, "ALL")
        return email_ids
    except Exception as e:
        return f'Error happens in retrieving email: {str(e)}'