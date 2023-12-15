from __future__ import annotations

import datetime
import json
import logging
import os
from typing import TYPE_CHECKING, Optional

import _activate_django  # noqa # type: ignore - This modifies global values  # noqa # type: ignore - This modifies global values
from common.constants import BASE_DIR, DOWNLOADED_FILES_DIR
from django.db import transaction
from games.models import Country, Game, GameGenre, GamePlatform, GamePlatformCountry, Genre, Platform
from json_file import JSONFile
from scrape.download_and_save import download_and_save

if TYPE_CHECKING:
    from typing import Any

BASE_GAMES_URL = "https://api.mobygames.com/v1/games?"
GAME_LIST_FOLDER = JSONFile(DOWNLOADED_FILES_DIR) / "platforms"
COUNTRY_FILE = JSONFile(BASE_DIR) / "countries" / "countries.json"
COUNTRIES = COUNTRY_FILE.parsed()


logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def download_and_import_platform_games(platform: Platform):
    """Download the list of games for a platform"""
    for offset in range(999):
        game_list_json_path = get_platform_games_json_path(platform.id, offset)

        if not game_list_json_path.exists():
            logger.info(f"Downloading List of games for {platform}, page {offset + 1}")
            download_and_save(BASE_GAMES_URL, game_list_json_path, {"offset": offset * 100, "platform": platform.id})

        # Download every game listed
        parsed_json = game_list_json_path.parsed()
        for game in parsed_json["games"]:
            extract_game(game, game_list_json_path.aware_mtime())
            download_game(game)
            import_game(game)

        if not len(parsed_json["games"]) == 100:
            break


def extract_game(game: dict[str, Any], data_timestamp: datetime.datetime):
    """Extract the information for a game from the game list, doing this will reduce the API calls needed by one per
    game"""
    game_json_path = get_game_json_path(game)
    if not game_json_path.up_to_date(data_timestamp):
        game_json_path.write(json.dumps(game))
        a_time = game_json_path.lstat().st_mtime
        m_time = data_timestamp.timestamp()
        os.utime(game_json_path, (a_time, m_time))


def download_game(game: dict[str, Any], minimum_info_timestamp: Optional[datetime.datetime] = None):
    """Download all of the information for a game"""
    for platform in game["platforms"]:
        game_json_path = get_game_platform_json_path(game, platform)
        if game_json_path.outdated(minimum_info_timestamp):
            if game_json_path.exists():
                download_type = "Updating"
            else:
                download_type = "Downloading"

            url = f"https://api.mobygames.com/v1/games/{game['game_id']}/platforms/{platform['platform_id']}?"

            logger.info(
                f"{download_type} {game['title']} ({game['game_id']}) for {platform['platform_name']} ({platform['platform_id']})"
            )
            download_and_save(url, game_json_path)


def get_game_json_path(game: dict[str, Any]) -> JSONFile:
    return JSONFile(DOWNLOADED_FILES_DIR / "games" / f"{game['game_id']}.json")


def get_game_platform_json_path(game: dict[str, Any], platform: dict[str, Any]) -> JSONFile:
    return JSONFile(
        DOWNLOADED_FILES_DIR / "games" / f"{game['game_id']}" / "platforms" / f"{platform['platform_id']}.json"
    )


def get_platform_games_json_path(platform: int, offset: int) -> JSONFile:
    return JSONFile(DOWNLOADED_FILES_DIR / "platforms" / f"{platform}" / f"{offset}.json")


def game_platforms_json_path(game: dict[str, Any], platform: dict[str, Any]) -> JSONFile:
    return JSONFile(
        DOWNLOADED_FILES_DIR / "games" / f"{game['game_id']}" / "platforms" / f"{platform['platform_id']}.json"
    )


def get_country_match(country: str) -> tuple[str, str, str]:
    for country_info in COUNTRIES:
        if country_info["name"] == country or country in country_info.get("alternative_names", []):
            return country_info["iso2"], country_info["emoji"], country_info["region"]

    raise ValueError(f"Country not found: {country}")


@transaction.atomic
def import_game(game: dict[str, Any]):
    """Import the information for a specific game"""

    game_json_path = get_game_json_path(game)
    info_timestamp = game_json_path.aware_mtime()

    # Check if game is already imported
    if Game.objects.filter(id=game["game_id"], info_modified_timestamp__gte=info_timestamp).exists():
        logger.info(f"Already imported: {game['game_id']} {game['title']}")
        return

    logger.info(f"Importing: {game['game_id']} {game['title']}")

    # Can't do this using .get because sample_cover returns None not an empty dict
    if game["sample_cover"] is None:
        image_url = None
    else:
        image_url = game["sample_cover"]["thumbnail_image"]

    # Import game
    game_object = Game.objects.get_or_create(
        id=game["game_id"],
        defaults={
            "id": game["game_id"],
            "name": game["title"],
            "image": image_url,
            "description": game["description"],
            "info_modified_timestamp": datetime.datetime.now().astimezone(),
            "info_timestamp": info_timestamp,
        },
    )[0]

    import_game_genres(game_object, game)
    import_game_platforms(game_object, game)


def import_game_genres(game_object: Game, game: dict[str, Any]):
    # Delete existing releases for this game
    GameGenre.objects.filter(game=game_object).delete()

    # Import all genres
    for genre in game["genres"]:
        genre_object = Genre.objects.get_or_create(id=genre["genre_id"], defaults={"genre": genre["genre_name"]})[0]
        GameGenre.objects.create(game=game_object, genre=genre_object)


def import_game_platforms(game_object: Game, game: dict[str, Any]):
    # Import all releases
    for platform in game["platforms"]:
        parsed_game_platforms = game_platforms_json_path(game, platform).parsed()

        for release in parsed_game_platforms["releases"]:
            platform_object = Platform.objects.get_or_create(
                id=platform["platform_id"], name=platform["platform_name"]
            )[0]
            game_platform = GamePlatform.objects.get_or_create(game=game_object, platform=platform_object)[0]

            for country in release["countries"]:
                country_code, flag, region = get_country_match(country)
                country_object = Country.objects.get_or_create(
                    name=country, code=country_code, flag=flag, region=region
                )[0]

                # Alternative data format that may make sql easier
                GamePlatformCountry.objects.get_or_create(game_platform=game_platform, country=country_object)


def main():
    for platform in Platform.objects.all().filter(imported=False):
        logger.info(f"Importing {platform.name}")
        download_and_import_platform_games(platform)

        platform.imported = True
        platform.save()


if __name__ == "__main__":
    main()
