import datetime
import logging

import _activate_django  # noqa # type: ignore - This modifies global values
from common.constants import DOWNLOADED_FILES_DIR
from games.models import Platform
from json_file import JSONFile
from scrape.download_and_save import download_and_save

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

PLATFORMS_URL = "https://api.mobygames.com/v1/platforms?"
PLATFORMS_JSON_PATH = JSONFile(DOWNLOADED_FILES_DIR) / "platforms.json"


def get_platforms():
    minimum_timestam = datetime.datetime.now().astimezone() - datetime.timedelta(days=1)
    if PLATFORMS_JSON_PATH.outdated(minimum_timestam):
        logger.info("Downloaded platforms.json")
        download_and_save(PLATFORMS_URL, PLATFORMS_JSON_PATH)


def import_platforms():
    for platform in PLATFORMS_JSON_PATH.parsed()["platforms"]:
        import_platform(platform["platform_id"], platform["platform_name"])


def import_platform(platform_id: int, platform_name: str):
    msg = f"Importing platform {platform_name} ({platform_id})"
    logger.info(msg)
    Platform.objects.get_or_create(name=platform_name, id=platform_id)


def main():
    get_platforms()
    import_platforms()


if __name__ == "__main__":
    main()
