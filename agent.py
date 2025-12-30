import ollama
import json
import requests
import time


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
    def __init__(self):
        pass
    
class chatter:
    def __init__(self):
        self.model = 'qwen3:14b'
        self.chatHistory = [{'role': 'system', 'content': 'You are a sophisticated AI Assistant. Your name is Corque. You are able to use tools to help users get information. You must use the tools when necessary. Do remember to do parallel function calls when needed.'}]
        self.weather = weatherTool()
        self.email = emailTool()
        self.tools = [self.weather.getWeather]

    



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
                    result = self.weather.getWeather(**call.function.arguments)
                else:
                    result = 'Unknown Tools'
                self.chatHistory.append({'role': 'tool',  'tool_name': call.function.name, 'content': str(result)})
            finalResponse = ollama.chat(
                model = self.model,
                messages=self.chatHistory,
                tools=self.tools
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

