from django.contrib import admin
from games.models import Country, Game, GameGenre, GamePlatform, GamePlatformCountry, Genre, LastScrape, Platform

admin.site.register(Game)
admin.site.register(GamePlatform)
admin.site.register(GamePlatformCountry)
admin.site.register(GameGenre)
admin.site.register(Genre)
admin.site.register(Platform)
admin.site.register(Country)
admin.site.register(LastScrape)
