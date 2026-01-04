import ollama
import json
import requests
import time
import smtplib
import imaplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()
emailUser = os.getenv("OTS_EMAIL_USER")
emailPass = os.getenv("OTS_EMAIL_PASS")
smtpServer = os.getenv("OTS_SMTP_SERVER")
imapServer = os.getenv("OTS_IMAP_SERVER")

class weatherTool:
    def getWeather(self, location):
        '''
        Retrieves the current weather and temperature for a specified location.(获取特定城市的天气)
        If you cannot find the weather for the specified location, respond with "Sorry, I couldn't find the weather for that location.

        Args:
            location (str): The geographical location (e.g., 'Pittsburgh, PA' or 'Shanghai'). 
                            This argument is required.
        
        Returns:
            str: A summary of the current weather. 
        '''
        def searchWeather(location):
            try:
                # jsonurl = f"https://wttr.in/{location}?format=j1"#'https://api.open-meteo.com/v1/forecast?latitude=31.2222&longitude=121.4581&current=temperature_2m,relative_humidity_2m'
                # jsonresponse = requests.get(jsonurl)
                startTime = time.time()
                url = f"https://wttr.in/{location}?format=3"
                response = requests.get(url,timeout=10)
                endTime = time.time()
                diff = endTime - startTime
                print(f"Request Takes: {diff} 秒") 
                return response.text
            except Exception as e:
                return f'Error happens in searching for weather: {str(e)}'
        return searchWeather(location)

class emailTool:
    def __init__(self,emailAddress,emailPassword,smtpServer,imapServer):
        self.emailAddress = emailAddress
        self.emailPassword = emailPassword
        self.smtpServer = smtpServer
        self.imapServer = imapServer
        
        
    def sendEmail(self,recipientEmail,subject,body):
        '''
        Sends an email to a specified recipient with a subject and message body. (向指定收件人发送电子邮件)
        If the email fails to send, respond with "Sorry, I was unable to send the email at this time."

        Args:
            recipientEmail (str): The complete email address of the recipient (e.g., 'example@gmail.com').
                                This argument is required.
            subject (str): The subject line of the email. It should be concise and relevant.
                        This argument is required.
            body (str): The main content or message of the email. 
                        This argument is required.

        Returns:
            str: A confirmation message if the email is sent successfully, or an error message otherwise.
        '''
        self.stmpOBJ = smtplib.SMTP_SSL(self.smtpServer, 465)
        self.stmpOBJ.login(self.emailAddress, self.emailPassword)
        numOfRetries = 3
        for i in range(numOfRetries):
            try:
                time.sleep(0.5)  # To avoid rapid successive connections
                MSG = MIMEText(body)
                MSG['Subject'] = subject
                MSG['From'] = self.emailAddress
                MSG['To'] = recipientEmail
                self.stmpOBJ.send_message(MSG)
                self.stmpOBJ.quit()
                return 'Email sent successfully.'
            except Exception as e:
                if i<numOfRetries-1:
                    print(f"Retrying to send email... Attempt {i+1}")
                    time.sleep(1)  # Wait before retrying
                    continue
                print(f"Failed to send email after {numOfRetries} attempts.")
                self.stmpOBJ.quit()
                return f'Error happens in sending email: {str(e)}'

    
class chatter:
    def __init__(self):
        self.model = 'qwen3:14b'
        self.chatHistory = [{'role': 'system', 'content': 'You are a sophisticated AI Assistant. Your name is Corque. You are able to use tools to help users get information. You must use the tools when necessary. Do remember to do parallel function calls when needed.'}]
        self.weather = weatherTool()
        self.email = emailTool('stephen_xu2005@126.com','JXYKm7S9tNhKZgUE','smtp.126.com','imap.126.com')
        self.tools = [self.weather.getWeather, self.email.sendEmail]

    



    def runAgent(self):
        userInput = input("User: ")
        self.chatHistory.append({'role': 'user', 'content': userInput})
        response = ollama.chat(
            model = self.model,
            messages=self.chatHistory,
            tools=self.tools
        )
        content = response.message.content
        self.chatHistory.append(response.message)
        if response.message.tool_calls:
            print("Using Tools......")
            print(response.message.tool_calls)
            for call in response.message.tool_calls:
                if call.function.name == 'getWeather':
                    try:
                        result = self.weather.getWeather(**call.function.arguments)
                    except Exception as e:
                        result = f'Sorry, I couldn\'t find the weather for that location. Error: {str(e)}'                    
                elif call.function.name == 'sendEmail':
                    try:
                        self.email.sendEmail(**call.function.arguments)
                        result = 'Email sent successfully.'
                    except Exception as e:
                        result = f'Sorry, I was unable to send the email at this time. Error: {str(e)}'
                else:
                    result = 'Unknown Tools'
                self.chatHistory.append({'role': 'tool',  'tool_name': call.function.name, 'content': str(result)})
            finalResponse = ollama.chat(
                model = self.model,
                messages=self.chatHistory,
                tools=self.tools,
                think=False
            )
            print(f'Assistant: {finalResponse.message.content}')
            self.chatHistory.append(finalResponse.message)
        else:
            print(f"Assistant: {content}")



def main():
    Corque = chatter()
    while True:
        Corque.runAgent()

if __name__ == "__main__":
    main()

