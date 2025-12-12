"""
Search Extension - Web search using SearxNG.

Provides web search capabilities through a SearxNG instance.
"""

from sources.tools.searxSearch import searxSearch
from config.settings import settings
from sdk.decorators import command


class SearchExtension:
    """
    Extension for web search functionality using SearxNG.
    """
    
    def __init__(self):
        # Initialize the underlying tool (SearXNG)
        base_url = getattr(settings, 'searxng_base_url', None) or "http://localhost:8080"
        self.tool = searxSearch(base_url=base_url)

    @command(
        description="Performs a web search using SearxNG.",
        arguments={
            "query": "The search query string.",
            "num_results": "Optional. Number of results to return (default: 5)."
        }
    )
    def web_search(self, query: str, num_results: int = 5) -> str:
        """
        Performs a web search using SearxNG.
        
        Args:
            query: The search query.
            num_results: Number of results to return (not yet implemented in tool).
            
        Returns:
            Search results as formatted string.
        """
        result = self.tool.execute([query], False)
        
        # Limit results if num_results is specified
        if num_results and result and "Error" not in result:
            results = result.split("\n\n")
            if len(results) > num_results:
                results = results[:num_results]
                result = "\n\n".join(results)
        
        return result

    @command(
        description="Checks if a URL is accessible and valid.",
        arguments={"url": "The URL to check."}
    )
    def check_url(self, url: str) -> str:
        """
        Checks if a URL is accessible.
        
        Args:
            url: The URL to check.
            
        Returns:
            Status of the URL (OK, 404, Forbidden, Paywall, etc.)
        """
        return self.tool.link_valid(url)

    @command(
        description="Checks multiple URLs for accessibility.",
        arguments={"urls": "A list of URLs to check."}
    )
    def check_urls(self, urls: list) -> list:
        """
        Checks multiple URLs.
        
        Args:
            urls: List of URLs to check.
            
        Returns:
            List of status strings for each URL.
        """
        return self.tool.check_all_links(urls)
