import urllib.parse
import urllib.request

from api_key import API_KEY


def build_request(url: str) -> urllib.request.Request:
    """Take a URL, add a User-Agent header, and return a Request object"""
    url = url + urllib.parse.urlencode({"api_key": API_KEY})
    return urllib.request.Request(url, headers={"User-Agent": "Scraper"})
