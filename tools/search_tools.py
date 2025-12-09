from crewai_tools import tool
from tavily import TavilyClient
from config.settings import settings

tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)

@tool
def web_search(query: str):
    """Search the web for the most relevant information about Salesforce topics."""
    results = tavily.search(query=query, max_results=5)
    return results
