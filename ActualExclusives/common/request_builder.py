import urllib.request


def build_request(url: str) -> urllib.request.Request:
    """Take a URL, add a User-Agent header, and return a Request object"""
    return urllib.request.Request(url, headers={"User-Agent": "Scraper"})
