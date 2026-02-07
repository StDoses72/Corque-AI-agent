import smtplib
import imaplib
import time
from datetime import datetime, date
from email import message_from_bytes
from email.header import decode_header
from email.mime.text import MIMEText
from email.policy import default
from email.utils import parsedate_to_datetime
from config.settings import settings
from langchain_core.tools import tool


@tool
def sendEmail(recipientEmail,subject,body,fromWho = 'XiangCheng Xu'):
    '''
    Sends an email to a specified recipient with a subject and message body. (向指定收件人发送电子邮件)
    If the email fails to send, return an error message.
    Remember, the body should not contain email closing signature or sender name.

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
def getUnReademail(targetDate: str = None) -> list:
    '''
    Retrieves emails received on a specific date from the inbox.
    Default is today if no date is provided.
    Date format: "YYYY-MM-DD" (e.g., "2026-02-05").
    If the email fails to retrieve, respond with "Sorry, I couldn't find the email at this time."
    Args:
        targetDate (str): The date to retrieve emails from. Default is today if no date is provided.
    Returns:
        list: A list of emails retrieved from the inbox. Each email is a dictionary with the following keys:
            - id: The email ID.
            - subject: The subject of the email.
            - from: The sender of the email.
            - to: The recipient of the email.
            - date: The date of the email.
            - body: The body of the email.
    '''
    imapOBJ = imaplib.IMAP4_SSL(settings.imapServer)
    imapOBJ.login(settings.emailUser, settings.emailPass)
    def _decode_header_value(value):
        if not value:
            return ""
        decoded_parts = decode_header(value)
        decoded_text = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_text.append(part.decode(encoding or "utf-8", errors="replace"))
            else:
                decoded_text.append(part)
        return "".join(decoded_text)

    def _extract_body(msg):
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    return part.get_content()
            return ""
        return msg.get_content()

    def _is_target_date(date_header, target_date):
        if not date_header:
            return False
        try:
            dt = parsedate_to_datetime(date_header)
        except Exception:
            return False
        if dt.tzinfo is not None:
            dt = dt.astimezone()
        return dt.date() == target_date

    try:
        imapOBJ.select("INBOX")
        if targetDate:
            try:
                target_date = datetime.strptime(targetDate, "%Y-%m-%d").date()
            except Exception:
                return "Sorry, I couldn't find the email at this time."
        else:
            target_date = date.today()

        since_str = target_date.strftime("%d-%b-%Y")
        status, email_ids = imapOBJ.search(None, f'(SINCE "{since_str}")')
        if status != "OK":
            return "Sorry, I couldn't find the email at this time."
        if not email_ids or not email_ids[0]:
            return []

        messages = []
        for email_id in email_ids[0].split():
            fetch_status, data = imapOBJ.fetch(email_id, "(BODY.PEEK[])")
            if fetch_status != "OK" or not data or not data[0]:
                continue
            raw_email = data[0][1]
            msg = message_from_bytes(raw_email, policy=default)
            if not _is_target_date(msg.get("Date"), target_date):
                continue

            messages.append({
                "id": email_id.decode("utf-8", errors="replace"),
                "subject": _decode_header_value(msg.get("Subject")),
                "from": _decode_header_value(msg.get("From")),
                "to": _decode_header_value(msg.get("To")),
                "date": _decode_header_value(msg.get("Date")),
                "body": _extract_body(msg),
            })

        return messages
    except Exception:
        return "Sorry, I couldn't find the email at this time."
    finally:
        try:
            imapOBJ.logout()
        except Exception:
            pass