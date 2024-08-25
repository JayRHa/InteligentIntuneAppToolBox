"""Handle bing search request."""

import requests
from loguru import logger


# from utils.code.web import request_get_async


class Bing:
    """Bing Search API."""

    ACCOUNT_URL = "https://api.bing.microsoft.com/v7.0/search"

    def __init__(self, secret: str) -> None:
        """Initializes a new instance of the Bing class."""
        self.secret = secret

    def get_search_results(self, query: str) -> dict:
        """Get search results from Bing."""
        headers = {"Ocp-Apim-Subscription-Key": self.secret}
        params = {
            "q": query,
            "textDecorations": True,
            "textFormat": "HTML",
            "responseFilter": "Webpages",
            "safeSearch": "strict",
            "setLang": "en",
        }
        try:
            response = requests.get(
                url=self.ACCOUNT_URL,
                headers=headers,
                params=params,
                timeout=20,
            )
            response.raise_for_status()
            response = response.json()
            response = response.get("webPages", {}).get("value", [])
            response = [i.get("snippet", "") for i in response]

            return response
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to call bing service: {e}")
            return {}
