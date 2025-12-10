from sources.tools.searxSearch import searxSearch
from config.settings import settings

class SearchExtension:
    def __init__(self):
        # Initialize the underlying tool (SearXNG)
        base_url = getattr(settings, 'searxng_base_url', None) or "http://localhost:8080"
        self.tool = searxSearch(base_url=base_url)
        
        # Define commands exposed by this extension
        self.commands = {
            "web_search": self.web_search
        }

    def web_search(self, query: str, num_results: int = 5):
        """
        Performs a web search using SearXNG.
        Args:
            query: The search query.
            num_results: Number of results to return.
        """
        return self.tool.execute([query], False)
