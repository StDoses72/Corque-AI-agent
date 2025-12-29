import ollama
import json
import requests
import time


class chatter:
    def __init__(self):
        self.model = 'qwen3:30b'
        self.chatHistory = [{'role': 'system', 'content': 'You are a sophisticated AI Assistant. Your name is Corque. You are able to use tools to help users get informationr. You must use the tools when necessary. Do remember to do parallel function calls when needed.'}]

def getWeather(location):
    '''
    Get the temperature of a location.When asking for weather information, must use this tool. 
    Note: This tool only accepts ONE location at a time. 
    If you need to check multiple places, call this tool multiple times.
    Args:
        location: The name of location
    Returns:
        The current temperature for the location 
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
            print(f"请求耗时: {diff} 秒") 
            return response.text
        except Exception as e:
            return f'查询天气时发生错误：{str(e)}'
    return searchWeather(location)



def runAgent(chatter):
    userInput = input("User: ")
    chatter.chatHistory.append({'role': 'user', 'content': userInput})
    response = ollama.chat(
        model = chatter.model,
        messages=chatter.chatHistory,
        tools=[getWeather]
    )
    content = response.message.content
    chatter.chatHistory.append(response.message)
    if response.message.tool_calls:
        print("工具调用中...")
        print(response.message.tool_calls)
        for call in response.message.tool_calls:
            if call.function.name == 'getWeather':
                result = getWeather(**call.function.arguments)
            else:
                result = 'Unknown Tools'
            chatter.chatHistory.append({'role': 'tool',  'tool_name': call.function.name, 'content': str(result)})
        finalResponse = ollama.chat(
            model = chatter.model,
            messages=chatter.chatHistory,
            tools=[getWeather]
        )
        print(f'Assistant: {finalResponse.message.content}')
        chatter.chatHistory.append(finalResponse.message)
    else:
        print(f"Assistant: {content}")



def main():
    Corque = chatter()
    while True:
        runAgent(Corque)

if __name__ == "__main__":
    main()

