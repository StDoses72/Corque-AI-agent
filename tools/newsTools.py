from tavily import TavilyClient
from config.settings import settings
from langchain_core.tools import tool

@tool
def dailyNewsSearch(query) -> str:
    '''
    This tool is used to search the web for daily news.
    It will return the most relevant news from the web.
    Use it to support your responses when the user asks for daily news.
    Args:
        query (str): The query to search the web for.
    Returns:
        str: The most relevant news from the web. Each news is a dictionary with the following keys:
            - url: The URL of the news.
            - title: The title of the news.
            - content: The content of the news.
    '''
    tavily_client = TavilyClient(api_key=settings.tavilyApiKey)
    response = tavily_client.search(query,topic="news",time_range="day")
    return response

def startingNewsSearch(topics: list[str]) -> str:
    '''
    This tool is used to search the web for news with topics that is set by the user when Corque is starting.
    It will return the most relevant news from the web with the topics.
    Args:
        topics (list[str]): The topics to search the web for. This argument is required.
    Returns:
        str: The most relevant news from the web with the topics. Each news is a dictionary with the following keys:
            - url: The URL of the news.
            - title: The title of the news.
            - content: The content of the news.
    '''
    tavily_client = TavilyClient(api_key=settings.tavilyApiKey)
    context = []
    for topic in topics:
        response = tavily_client.search(topic,topic="news",time_range="day")
        context.append({
            "topic": topic,
            "context":[{
                "url":result["url"], "title":result["title"], "content":result["content"]} for result in response["results"]
                ]
                })
    return context