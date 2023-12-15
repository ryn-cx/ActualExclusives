import logging
from datetime import datetime, timedelta

import _activate_django  # noqa # type: ignore - This modifies global values
from common.constants import DOWNLOADED_FILES_DIR
from extended_path import ExtendedPath
from games.models import LastScrape
from json_file import JSONFile
from scrape.download_and_save import download_and_save

BASE_URL = "https://api.mobygames.com/v1/games/recent?"
RECENT_FOLDER = ExtendedPath(DOWNLOADED_FILES_DIR) / "recent"
DATETIME = datetime.today().strftime("%Y-%m-%d")
CURRENT_DATE_FOLDER = RECENT_FOLDER / DATETIME

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def download(age: int):
    for offset in range(999):
        json_path = JSONFile(CURRENT_DATE_FOLDER / f"{offset}.json")

        # If the file does not exist download it
        if not json_path.exists():
            logger.info(f"Downloading Recent Games Page {offset + 1}")
            download_and_save(BASE_URL, json_path, {"offset": offset * 100, "age": age, "format": "normal"})

        parsed_json = json_path.parsed()

        # Check if this is the last page so downloads can stop
        if not len(parsed_json["games"]) == 100:
            logger.info("Download Complete: List of recent games downloaded")
            break


def recreate_last_scrape():
    folders = [f for f in RECENT_FOLDER.iterdir() if f.is_dir()]
    if folders:
        # Find the oldest file in oldest_folder
        if oldest_folder := min(folders, default=None):
            if files := list(oldest_folder.iterdir()):
                if oldest_file := min(files, default=None):
                    LastScrape.objects.create(datetime=oldest_file.aware_mtime())


def main():
    # If last scrape does not exist try to recreate it from existing files
    if not LastScrape.objects.exists():
        recreate_last_scrape()

    # If there really was no last scrape download the last 21 days
    if not LastScrape.objects.exists():
        days = 21
    else:
        last_scrape = LastScrape.objects.latest("datetime")
        if last_scrape.datetime > (datetime.now() - timedelta(days=1)).astimezone():
            logger.warning("Updating skipped: Last download was withing 24 hours")
            return

        # I don't know exactly how days are calculated and when this will be run, but a 2 day buffer should be enough
        # for every possible situation
        days = (datetime.now().astimezone() - last_scrape.datetime).days + 2

    logger.info(f"Downloading last {days} days of recent games")
    download(days)

    LastScrape.objects.create(datetime=datetime.now().astimezone())


if __name__ == "__main__":
    main()
    # TODO: Actual updating, go through every json file, find outdated, update them, rename/move json file, ignore
    # buffer days etc
