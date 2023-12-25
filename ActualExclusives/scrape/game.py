"""Class for managing game information."""
from __future__ import annotations

import datetime
import json
import logging
import os
from typing import TYPE_CHECKING

import _activate_django  # type: ignore # noqa: F401, PGH003 - Modified global path
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


class GameManager:
    """Class for managing game information."""

    def __init__(self, game_id: int) -> None:
        """Initialize the game manager."""
        self.game_id = game_id
        self.game_json_path = JSONFile(DOWNLOADED_FILES_DIR / "games" / f"{self.game_id}.json")

    def game_platform_json_path(self, platform_id: int) -> JSONFile:
        """Path for the platform JSON file."""
        return JSONFile(DOWNLOADED_FILES_DIR, "games", self.game_id, "platforms", f"{platform_id}.json")

    def game_platform_json_url(self, platform_id: int) -> str:
        """Url for the platform JSON file."""
        return f"https://api.mobygames.com/v1/games/{self.game_id}/platforms/{platform_id}?"

    def game_json_url(self) -> str:
        """Url for the game JSON file."""
        return f"https://api.mobygames.com/v1/games/{self.game_id}?"

    def extract_game_json(self, game_json: dict[str, Any], data_timestamp: datetime.datetime) -> None:
        """Save the game json to the file system."""
        game_json_path = self.game_json_path
        if not game_json_path.up_to_date(data_timestamp):
            game_json_path.write(json.dumps(game_json))
            a_time = game_json_path.lstat().st_mtime
            m_time = data_timestamp.timestamp()
            os.utime(game_json_path, (a_time, m_time))

    def download_game(self, minimum_info_timestamp: datetime.datetime | None = None) -> None:
        """Download the game information."""
        game_json_path = self.game_json_path
        if game_json_path.outdated(minimum_info_timestamp):
            download_type = "Downloading Update" if game_json_path.exists() else "Downloading Initial"

            logger.info("%s %s", download_type, self.game_id)

            url = self.game_json_url()
            download_and_save(url, game_json_path)

    def download_game_platforms(self, minimum_info_timestamp: datetime.datetime | None = None) -> None:
        """Download all of the platform information for a game."""
        game_json_parsed = self.game_json_path.parsed_cached()
        for platform in game_json_parsed["platforms"]:
            game_json_path = self.game_platform_json_path(platform["platform_id"])
            if game_json_path.outdated(minimum_info_timestamp):
                download_type = "Updating" if game_json_path.exists() else "Downloading"

                logger.info(
                    "%s %s (%s) for %s (%s)",
                    download_type,
                    game_json_parsed["title"],
                    game_json_parsed["game_id"],
                    platform["platform_name"],
                    platform["platform_id"],
                )

                url = self.game_platform_json_url(platform["platform_id"])
                download_and_save(url, game_json_path)

    @transaction.atomic
    def import_game(
        self,
        info_timestamp: datetime.datetime | None = None,
        info_modified_timestamp: datetime.datetime | None = None,
    ) -> None:
        """Import the information for a specific game."""
        game = self.game_json_path.parsed_cached()
        game_string = f"{self.game_id}. {game['title']}"

        logger.info("Importing: %s", game_string)

        game_object = Game.objects.filter(id=self.game_id).first()

        # Check if game is already imported
        if game_object and game_object.is_up_to_date(info_timestamp, info_modified_timestamp):
            logger.info("Importing::Up To Date: %s", game_string)
            return

        logger.info("Importing::Outdated: %s", game_string)

        # Can't do this using .get because sample_cover returns None not an empty dict
        image_url = None if game["sample_cover"] is None else game["sample_cover"]["thumbnail_image"]

        # Use game["game_id"] instead of self.game_id just in case there is ever a mismatch due to some silly mistake
        game_object = Game.objects.get_or_create(
            id=game["game_id"],
            defaults={
                "id": game["game_id"],
                "name": game["title"],
                "image": image_url,
                "description": game["description"],
                "info_modified_timestamp": datetime.datetime.now().astimezone(),
                "info_timestamp": self.game_json_path.aware_mtime(),
            },
        )[0]

        self.import_game_genres(game_object, game)
        self.import_game_platforms(game_object, game)

    def import_game_genres(self, game_object: Game, game: dict[str, Any]) -> None:
        """Import all of the genres for a game."""
        GameGenre.objects.filter(game=game_object).delete()

        # Import all genres
        for genre in game["genres"]:
            genre_object = Genre.objects.get_or_create(id=genre["genre_id"], defaults={"genre": genre["genre_name"]})[0]
            GameGenre.objects.create(game=game_object, genre=genre_object)

    def import_game_platforms(self, game_object: Game, game: dict[str, Any]) -> None:
        """Import all of the platforms for a game."""
        for platform in game["platforms"]:
            parsed_game_platforms = self.game_platform_json_path(platform["platform_id"]).parsed()

            for release in parsed_game_platforms["releases"]:
                platform_object = Platform.objects.get_or_create(
                    id=platform["platform_id"],
                    name=platform["platform_name"],
                )[0]
                game_platform = GamePlatform.objects.get_or_create(game=game_object, platform=platform_object)[0]

                for country in release["countries"]:
                    country_code, flag, region = self.get_country_match(country)
                    country_object = Country.objects.get_or_create(
                        name=country,
                        code=country_code,
                        flag=flag,
                        region=region,
                    )[0]

                    GamePlatformCountry.objects.get_or_create(game_platform=game_platform, country=country_object)

    def update_game(
        self,
        game: dict[str, Any],
        data_timestamp: datetime.datetime,
        minimum_info_timestamp: datetime.datetime | None = None,
        minimum_info_modified_timestamp: datetime.datetime | None = None,
    ) -> None:
        """Update the information for a game."""
        self.extract_game_json(game, data_timestamp)
        self.download_game_platforms(minimum_info_timestamp)
        self.import_game(minimum_info_timestamp, minimum_info_modified_timestamp)

    def get_country_match(self, country: str) -> tuple[str, str, str]:
        """Get the country code, flag, and region for a country."""
        for country_info in COUNTRIES:
            if country_info["name"] == country or country in country_info.get("alternative_names", []):
                return country_info["iso2"], country_info["emoji"], country_info["region"]

        msg = f"Country not found: {country}"
        raise ValueError(msg)
