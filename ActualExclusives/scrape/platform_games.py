"""Download and import the games for a platform."""
from __future__ import annotations

import logging

import _activate_django  # type: ignore # noqa: F401, PGH003 - Modified global path
from common.constants import BASE_DIR, DOWNLOADED_FILES_DIR
from games.models import Platform
from json_file import JSONFile

from scrape.download_and_save import download_and_save
from scrape.game import GameManager

BASE_GAMES_URL = "https://api.mobygames.com/v1/games?"
GAME_LIST_FOLDER = JSONFile(DOWNLOADED_FILES_DIR) / "platforms"
COUNTRY_FILE = JSONFile(BASE_DIR) / "countries" / "countries.json"
COUNTRIES = COUNTRY_FILE.parsed()
RESULTS_PER_PAGE = 100


logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def download_and_import_platform_games(platform: Platform) -> None:
    """Download the list of games for a platform."""
    offset = 0
    while True:
        # Your code here
        offset += 1
        game_list_json_path = platform_games_json_path(platform.id, offset)

        if not game_list_json_path.exists():
            logger.info("Downloading Games: %s, page %s", platform, offset + 1)
            download_and_save(BASE_GAMES_URL, game_list_json_path, {"offset": offset * 100, "platform": platform.id})

        # Download every game listed
        parsed_json = game_list_json_path.parsed()
        for game in parsed_json["games"]:
            game_manager = GameManager(game["game_id"])
            game_manager.extract_game_json(game, game_list_json_path.aware_mtime())
            game_manager.download_game_platforms()
            game_manager.import_game()

        if len(parsed_json["games"]) != RESULTS_PER_PAGE:
            break


def platform_games_json_path(platform: int, offset: int) -> JSONFile:
    """Path for the platform JSON file."""
    return JSONFile(DOWNLOADED_FILES_DIR / "platforms" / f"{platform}" / f"{offset}.json")


def main() -> None:
    """Download and import the list of games for a platform."""
    for platform in Platform.objects.all().filter(imported=False):
        logger.info("Importing Platform: %s", platform.name)
        download_and_import_platform_games(platform)
        platform.imported = True
        platform.save()


if __name__ == "__main__":
    main()
