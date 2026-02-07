from tavily import TavilyClient
from config.settings import settings
from langchain_core.tools import tool



@tool
def basicWebSearch(query) -> str:
    '''
    This tool is used to search the web for information.
    It will return the most relevant information from the web.
    Use it to support your responses when the user asks for information that is not available in your knowledge base or can not be done with other tools.
    Args:
        query (str): The query to search the web for.
    Returns:
        str: The most relevant information from the web.
    '''
    tavily_client = TavilyClient(api_key=settings.tavilyApiKey)
    response = tavily_client.search(query,max_results=5)
    return response