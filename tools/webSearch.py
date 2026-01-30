from tavily import TavilyClient
from config.settings import settings

client = TavilyClient(api_key=settings.tavilyApiKey)

def basicWebSearch(query):
    '''
    '''
    results = client.search(query)
    return results