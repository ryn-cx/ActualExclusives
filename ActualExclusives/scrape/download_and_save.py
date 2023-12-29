"""Function to download a file and save it to the file system."""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from typing import TYPE_CHECKING

from api_key import API_KEY

if TYPE_CHECKING:
    from json_file import JSONFile


def download_and_save(url: str, file_path: JSONFile, params: dict[str, str | int] | None = None) -> None:
    """Download a file and save it to the file system."""
    if not params:
        params = {}

    url = url + urllib.parse.urlencode({**params, "api_key": API_KEY})

    # This is completely pointless, but it SHOULD fullfills a ruff linter requirement, unfortunately it does not work
    # even though this code was copied directly from the documentation.
    if not url.startswith(("http:", "https:")):
        msg = "URL must start with 'http:' or 'https:'"
        raise ValueError(msg)

    request = urllib.request.Request(url, headers={"User-Agent": "Scraper"})  # noqa: S310 - This linter is bugged
    content = urllib.request.urlopen(request).read().decode("utf-8")  # noqa: S310 - This linter is bugged

    # Load the content to verify it is valid JSON before saving it
    json.loads(content)
    file_path.write(content)

    # Always sleep 10 seconds after every download according to the API requirements
    time.sleep(10)
    # Don't bother returning the response and just reload it from the file every time because the 10 second wait makes
    # the difference in performance negligible
