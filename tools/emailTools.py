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
    If the email fails to send, respond with "Sorry, I was unable to send the email at this time."

    Args:
        recipientEmail (str): The complete email address of the recipient (e.g., 'example@gmail.com').
                            This argument is required.
        subject (str): The subject line of the email. It should be concise and relevant.
                    This argument is required.
        body (str): The main content or message of the email. 
                    This argument is required. You should add the greeting at the beginning of the body.
        fromWho (str): The name of the sender. Default is 'XiangCheng Xu'.

    Returns:
        str: A confirmation message if the email is sent successfully, or an error message otherwise.
    '''
    stmpOBJ = smtplib.SMTP_SSL(settings.smtpServer, 465, local_hostname='localhost')
    stmpOBJ.login(settings.emailUser, settings.emailPass)
    numOfRetries = 3
    for i in range(numOfRetries):
        try:
            time.sleep(0.5)  # To avoid rapid successive connections
            fullBody = f'{body} \n\nBest regards,\n{fromWho}'
            MSG = MIMEText(fullBody)
            MSG['Subject'] = subject
            MSG['From'] = settings.emailUser
            MSG['To'] = recipientEmail
            stmpOBJ.send_message(MSG)
            stmpOBJ.quit()
            return 'Email sent successfully.'
        except Exception as e:
            if i<numOfRetries-1:
                print(f"Retrying to send email... Attempt {i+1}")
                time.sleep(1)  # Wait before retrying
                continue
            print(f"Failed to send email after {numOfRetries} attempts.")
            stmpOBJ.quit()
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