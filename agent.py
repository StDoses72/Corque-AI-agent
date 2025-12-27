import ollama
import json
import requests
import time

sysPrompt = """
你是一个本地助理。你可以调用以下工具：
1. getWeather(location): 获取指定城市天气。

如果用户要求执行这些操作，请只输出以下 JSON 格式，不要说任何废话：
{"tool": "函数名", "args": {"参数名": "参数值"}}
如果你判断内容不存在于提供的工具中，你可以直接回答用户的问题，而不需要调用任何工具。
"""
class chatter:
    def __init__(self,systemPrompt=sysPrompt):
        self.model = 'gpt-oss:20b'
        self.chatHistory = [{'role': 'system', 'content': systemPrompt}]
        self.systemPrompt = systemPrompt

def getWeather(location):
    jsonurl = f"https://wttr.in/{location}?format=j1"#'https://api.open-meteo.com/v1/forecast?latitude=31.2222&longitude=121.4581&current=temperature_2m,relative_humidity_2m'
    jsonresponse = requests.get(jsonurl)
    startTime = time.time()
    url = f"https://wttr.in/{location}?format=3"
    response = requests.get(url)
    endTime = time.time()
    diff = endTime - startTime
    print(f"请求耗时: {diff} 秒") 
    return response.text



def runAgent(chatter):
    userInput = input("User: ")
    response = ollama.chat(
        model = chatter.model,
        messages=chatter.chatHistory+[{'role': 'user', 'content': userInput}]
    )
    chatter.chatHistory.append({'role': 'assistant', 'content': response['message']['content']})
    chatter.chatHistory.append({'role': 'user', 'content': userInput})
    content = response['message']['content']
    print(f"Assistant: {content}")

def getJsonToFunc(content):
    jsonIndexStart = content.find('{')
    jsonIndexEnd = content.rfind('}') + 1

    jsonInfo = content[jsonIndexStart:jsonIndexEnd]
    command = json.loads(jsonInfo)
    return command

def main():
    Corque = chatter()
    while True:
        runAgent(Corque)

if __name__ == "__main__":
    main()

