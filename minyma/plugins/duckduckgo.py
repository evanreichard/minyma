import json
import requests
from bs4 import BeautifulSoup
from minyma.plugin import MinymaPlugin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0)"
    " Gecko/20100101 Firefox/105.0",
}

class DuckDuckGoPlugin(MinymaPlugin):
    """Search DuckDuckGo"""

    def __init__(self, config):
        self.config = config
        self.name = "duck_duck_go"
        self.functions = [self.search_duck_duck_go]

    def search_duck_duck_go(self, query: str):
        """Search DuckDuckGo"""
        resp = requests.get("https://html.duckduckgo.com/html/?q=%s" % query, headers=HEADERS)
        soup = BeautifulSoup(resp.text, features="html.parser")

        # Get Results
        results = []
        for item in soup.select(".result > div"):
            title_el = item.select_one(".result__title > a")
            title = title_el.text.strip() if title_el and title_el.text is not None else ""

            description_el = item.select_one(".result__snippet")
            description = description_el.text.strip() if description_el and description_el.text is not None else ""

            results.append({"title": title, "description": description})

        # Derive Metadata (Title)
        metadata = {
            "titles": list(
                map(
                    lambda x: x.get("title"),
                    results[:5]
                )
            )
        }

        return {
            "content": json.dumps(results[:5]),
            "metadata": metadata,
            "error": None
        }
