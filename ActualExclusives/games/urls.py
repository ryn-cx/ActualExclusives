"""Game URL Configuration."""
from django.urls import path

from games import views

urlpatterns = [
    # This is slightly redundant, but it makes having parameters on the index page prettier
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("games", views.games, name="games"),
]
