"""Download the list of recent games from MobyGames and import it."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

import _activate_django  # type: ignore # noqa: F401, PGH003 - Modified global path
from common.constants import DOWNLOADED_FILES_DIR
from games.models import LastScrape
from json_file import JSONFile
from paved_path import PavedPath
from scrape.download_and_save import download_and_save
from scrape.game import GameManager

BASE_URL = "https://api.mobygames.com/v1/games/recent?"
RECENT_FOLDER = PavedPath(DOWNLOADED_FILES_DIR) / "recent"
COMPLETED_RECENT_FOLDER = PavedPath(DOWNLOADED_FILES_DIR) / "completed_recent"

RESULTS_PER_PAGE = 100

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def download(date_folder: PavedPath, age: int) -> None:
    """Download the list of recent games from MobyGames."""
    for offset in range(999):
        json_path = JSONFile(date_folder / f"{offset}.json")

        # If the file does not exist download it
        if not json_path.exists():
            logger.info("Downloading Recent Games Page %s", (offset + 1))
            download_and_save(BASE_URL, json_path, {"offset": offset * 100, "age": age, "format": "normal"})

        parsed_json = json_path.parsed()

        # Check if this is the last page so downloads can stop
        if len(parsed_json["games"]) != RESULTS_PER_PAGE:
            logger.info("Download Complete: List of recent games downloaded")
            break


def import_last_scrape_date(*folders: PavedPath) -> None:
    """Get the date from the last scrape."""
    for folder in folders:
        if last_good_scrape := newest_scrape_from_folder(folder):
            LastScrape.objects.create(datetime=last_good_scrape)
            break


def newest_scrape_from_folder(recent_dir: PavedPath, folder_index: int = 0) -> datetime | None:
    """Get the date from the specified folder."""
    if folders := [f for f in recent_dir.iterdir() if f.is_dir()]:
        newest_folders = sorted(folders, key=lambda f: f.aware_mtime(), reverse=True)

        # Check if the folder for the current index exists
        if folder_index < len(newest_folders):
            newest_folder = newest_folders[folder_index]

            if files := list(newest_folder.iterdir()):
                newest_file = max(files, key=lambda f: f.aware_mtime())
                parsed_file = JSONFile(newest_file).parsed()
                # Check if this is the last page or if there are more pages that did not download
                if len(parsed_file["games"]) != RESULTS_PER_PAGE:
                    return newest_file.aware_mtime()

                # If there are more pages that did not download check the next folder
                return newest_scrape_from_folder(recent_dir, folder_index + 1)
    return None


def main() -> None:
    """Download the list of recent games from MobyGames and import it."""
    current_datetime = RECENT_FOLDER / datetime.now().astimezone()

    # If last scrape does not exist try to recreate it from existing files
    if not LastScrape.objects.exists():
        import_last_scrape_date(RECENT_FOLDER, COMPLETED_RECENT_FOLDER)

    # If there really was no last scrape download the last 21 days
    if not LastScrape.objects.exists():
        days = 21
    else:
        last_scrape = LastScrape.objects.latest("datetime")
        if last_scrape.datetime > (datetime.now().astimezone() - timedelta(days=1)).astimezone():
            logger.warning("Updating skipped: Last download was withing 24 hours")
            return

        # I don't know exactly how days are calculated and when this will be run, but a 2 day buffer should be enough
        # for every possible situation
        days = (datetime.now().astimezone() - last_scrape.datetime).days + 2

    logger.info("Downloading last %s days of recent games", days)
    download(current_datetime, days)

    LastScrape.objects.create(datetime=datetime.now().astimezone())

    for date_folder in RECENT_FOLDER.iterdir():
        # Make sure file is at laeast 48 horus old to make sure I don't end up doing double downloads because of the 2
        # day buffer
        if date_folder.aware_mtime() < (datetime.now().astimezone() - timedelta(days=2)).astimezone():
            for file_path in date_folder.iterdir():
                json_file = JSONFile(file_path)
                parsed_json = json_file.parsed()
                for game in parsed_json["games"]:
                    game_manager = GameManager(game["game_id"])
                    game_manager.extract_game_json(game, json_file.aware_mtime())
                    game_manager.download_game_platforms(json_file.aware_mtime())
                    game_manager.import_game(json_file.aware_mtime())


if __name__ == "__main__":
    main()
    # TODO: Actual updating, go through every json file, find outdated, update them, rename/move json file, ignore
    # buffer days etc
