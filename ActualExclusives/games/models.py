"""Models for the games app."""
from django.db import models
from great_django_family import ModelWithId, ModelWithTimestamps


class Genre(models.Model):
    """Genre model."""

    id = models.IntegerField(primary_key=True)  # noqa: A003 - Name of id is good
    genre = models.CharField(max_length=200, unique=True)

    def __str__(self) -> str:
        """Genre as string."""
        return self.genre


class Platform(models.Model):
    """Platform model."""

    id = models.IntegerField(primary_key=True)  # noqa: A003 - Name of id is good
    name = models.CharField(max_length=200, unique=True)
    imported = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Platform as string."""
        return self.name


class Country(models.Model):
    """Country model."""

    id = models.AutoField(primary_key=True)  # noqa: A003 - Name of id is good
    region = models.CharField(max_length=200)
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=2)
    flag = models.CharField(max_length=32)

    def __str__(self) -> str:
        """Country as string."""
        return self.name


class Game(ModelWithTimestamps):
    """Game model."""

    id = models.IntegerField(primary_key=True)  # noqa: A003 - Name of id is good
    name = models.CharField(max_length=200)
    image = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    gameplatform_set: models.QuerySet["GamePlatform"]

    def __str__(self) -> str:
        """Game as string."""
        return self.name


class GamePlatform(ModelWithId):
    """GamePlatform model."""

    gameplatformcountry_set: models.QuerySet["GamePlatformCountry"]

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """GamePlatform as string."""
        return f"{self.game} - {self.platform}"


class GamePlatformCountry(ModelWithId):
    """GamePlatformCountry model."""

    game_platform = models.ForeignKey(GamePlatform, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """GamePlatformCountry as string."""
        return f"{self.game_platform} - {self.country}"


class GameGenre(ModelWithId):
    """GameGenre model."""

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """GameGenre as string."""
        return f"{self.game} - {self.genre}"


class LastScrape(ModelWithId):
    """LastScrape model."""

    datetime = models.DateTimeField()

    def __str__(self) -> str:
        """LastScrape as string."""
        return f"{self.datetime}"
