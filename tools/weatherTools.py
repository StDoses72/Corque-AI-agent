import requests
import time
from langchain_core.tools import tool

@tool
def getWeather(location) -> str:
    '''
    Retrieves the current or the forecasted weather and temperature for a specified location.(获取特定城市的天气)
    If you cannot find the weather for the specified location, respond with "Sorry, I couldn't find the weather for that location.

    Args:
        location (str): The geographical location (e.g., 'Pittsburgh, PA' or 'Shanghai'). 
                        This argument is required.
        forecast (bool): Whether to get the forecasted weather. Default is False.
    
    Returns:
        str: A summary of the current weather. 
    '''
    def searchWeather(location,forecast=False):
        try:
            # jsonurl = f"https://wttr.in/{location}?format=j1"#'https://api.open-meteo.com/v1/forecast?latitude=31.2222&longitude=121.4581&current=temperature_2m,relative_humidity_2m'
            # jsonresponse = requests.get(jsonurl)
            startTime = time.time()
            if forecast:
                url = f"https://wttr.in/{location}?format=j1"
            else:
                url = f"https://wttr.in/{location}?format=3"
            response = requests.get(url,timeout=10)
            endTime = time.time()
            diff = endTime - startTime
            print(f"Request Takes: {diff} 秒") 
            return response.text
        except Exception as e:
            return f'Error happens in searching for weather: {str(e)}'
    return searchWeather(location)