import json
import time
import urllib.parse
import urllib.request
from typing import TYPE_CHECKING, Optional

from api_key import API_KEY

if TYPE_CHECKING:
    from extended_path import ExtendedPath


def download_and_save(url: str, file_path: "ExtendedPath", params: Optional[dict[str, str | int]] = None) -> None:
    start_time = time.time()
    if not params:
        params = {}

    url = url + urllib.parse.urlencode({**params, "api_key": API_KEY})
    request = urllib.request.Request(url, headers={"User-Agent": "Scraper"})

    content = urllib.request.urlopen(request).read().decode("utf-8")
    # Load the content to verify it is valid JSON before saving it
    json.loads(content)
    file_path.write(content)

    # Always sleep 10 seconds after every download according to the API requirements
    sleep_time = 10 - (time.time() - start_time)
    if sleep_time > 0:
        time.sleep(sleep_time)
    # Don't bother returning the response and just reload it from the file every time because the 10 second wait makes
    # the difference in performance negligible
