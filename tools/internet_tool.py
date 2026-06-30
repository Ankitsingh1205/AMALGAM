import requests
from urllib.parse import urlencode

from config import settings


class InternetTool:

    name = "internet"

    def search(self, query: str):

        try:

            response = requests.get(
                settings.INTERNET_SEARCH_URL + "?" + urlencode({"q": query}),
                timeout=settings.INTERNET_TIMEOUT
            )

            return f"Connected (HTTP {response.status_code})"

        except Exception as e:

            return f"Internet Error: {e}"
