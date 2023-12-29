"""App config for the games app."""
from django.apps import AppConfig


class GamesConfig(AppConfig):
    """App config so Django can load games."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "games"
