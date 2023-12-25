from django.db import models
from great_django_family import ModelWithIdAndTimestamp


class Genre(models.Model):
    id = models.IntegerField(primary_key=True)
    genre = models.CharField(max_length=200, unique=True)

    def __str__(self) -> str:
        return self.genre


class Platform(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    imported = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    region = models.CharField(max_length=200)
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=2)
    flag = models.CharField(max_length=32)

    def __str__(self) -> str:
        return self.name


class Game(ModelWithIdAndTimestamp):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    image = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    gameplatform_set: models.QuerySet["GamePlatform"]

    def __str__(self) -> str:
        return self.name


class GamePlatform(models.Model):
    gameplatformcountry_set: models.QuerySet["GamePlatformCountry"]

    id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.game} - {self.platform}"


class GamePlatformCountry(models.Model):
    id = models.AutoField(primary_key=True)
    game_platform = models.ForeignKey(GamePlatform, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.game_platform} - {self.country}"


class GameGenre(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.game} - {self.genre}"


class LastScrape(models.Model):
    id = models.AutoField(primary_key=True)
    datetime = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.datetime}"
