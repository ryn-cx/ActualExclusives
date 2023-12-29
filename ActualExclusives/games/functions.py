"""Functions for the games app."""
from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count, Q, QuerySet

from games.models import Country, Game, GamePlatform, Platform

if TYPE_CHECKING:
    from django.forms import BaseFormSet

    from games.forms import SelectForm


def platform_form_exclusive(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    """Filter the queryset for games that are platform exclusive.

    Args:
    ----
        form: The form that was submitted.
        gp: The queryset to use for filtering.

    Returns:
    -------
        A queryset that is filtered for games that are platform exclusive.
    """
    platforms = Platform.objects.exclude(id__in=form.cleaned_data["platforms"])

    # Get all games that are on this platform
    exclusive_games = Game.objects.exclude(gameplatform__platform__in=platforms)

    # Count the number of platforms each game is on
    exclusive_games = exclusive_games.annotate(counter=Count("gameplatform"))

    # Filter out games that do not have the right number of platforms
    exclusive_games = exclusive_games.filter(counter=len(form.cleaned_data["platforms"]))

    if form.cleaned_data["platform_include"] == "Yes":
        return gp.filter(game__in=exclusive_games)

    # If platform_include is "No"
    return gp.exclude(game__in=exclusive_games)


def platform_form_and(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    """Get a queryset of GamePlatform objects that are on the given platforms.

    Args:
    ----
        form: The form that was submitted.
        gp: The queryset to use for filtering.

    Returns:
    -------
        A queryset of GamePlatform objects that are on the spcified platforms.
    """
    # Get a list of all of the games on that platform/in that region
    game = Game.objects
    for platform in form.cleaned_data["platforms"]:
        game = game.filter(gameplatform__platform=platform)

    if form.cleaned_data["platform_include"] == "Yes":
        return gp.filter(game__in=game, platform__in=form.cleaned_data["platforms"])

    # If platform_include is "No"
    return gp.exclude(game__in=game)


def platform_form_or(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    """Filter the queryset for games that are on at least one platform.

    Args:
    ----
        form: The form that was submitted.
        gp: The queryset to use for filtering.

    Returns:
    -------
        A queryset that is filtered for games that are on at least one platform.
    """
    if form.cleaned_data["platform_include"] == "Yes":
        return gp.filter(platform__in=form.cleaned_data["platforms"])

    # If platform_include is "No"
    # Get a list of all of the games on that platform
    game = Game.objects.filter(gameplatform__platform__in=form.cleaned_data["platforms"])

    return gp.exclude(game__in=game)


def platform_form(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    """Filter the queryset using the platform parameters.

    Args:
    ----
        form: The form that was submitted.
        gp: The queryset to use for filtering.

    Returns:
    -------
        A queryset using the platform parameters.
    """
    if form.cleaned_data["platform_search_type"] == "And":
        return platform_form_and(form, gp)
    if form.cleaned_data["platform_search_type"] == "Or":
        return platform_form_or(form, gp)
    if form.cleaned_data["platform_search_type"] == "Exclusive":
        return platform_form_exclusive(form, gp)

    msg = f"Unknown platform_search_type {form.cleaned_data['platform_search_type']}"
    raise ValueError(msg)


def country_form_exclusive(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    """Filter the queryset for games that are country exclusive.

    Args:
    ----
        form: The form that was submitted.
        gp: The queryset to use for filtering.

    Returns:
    -------
        A queryset that is filtered for games that are country exclusive.
    """
    other_countries = Country.objects.exclude(id__in=form.cleaned_data["countries"])

    # Filter based on the video games
    exclusive_games = Game.objects.filter(
        Q(gameplatform__in=gp) & ~Q(gameplatform__gameplatformcountry__country__in=other_countries),
    )

    if form.cleaned_data["platform_include"] == "Yes":
        return gp.filter(game__in=exclusive_games)

    # If platform_include is "No"
    return gp.exclude(game__in=exclusive_games)


def country_form_and(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    """Get a queryset of GamePlatform objects that are in the spcified countires.

    Args:
    ----
        form: The form that was submitted.
        gp: The queryset to use for filtering.

    Returns:
    -------
        A queryset of GamePlatform objects that are in the spcified countires.
    """
    for country in form.cleaned_data["countries"]:
        if form.cleaned_data["country_include"] == "Yes":
            exclusive_games = Game.objects.filter(
                Q(gameplatform__in=gp) & Q(gameplatform__gameplatformcountry__country=country),
            )

            return gp.filter(game__in=exclusive_games)

        # If platform_include is "No"
        exclusive_games = Game.objects.filter(
            Q(gameplatform__in=gp) & ~Q(gameplatform__gameplatformcountry__country=country),
        )

        return gp.filter(gameplatformcountry__country=country)

    # If there are no countries nothing needs to be done
    return gp


def country_form_or(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    """Filter the queryset for games that are in at least one country.

    Args:
    ----
        form: The form that was submitted.
        gp: The queryset to use for filtering.

    Returns:
    -------
        A queryset that is filtered for games that are in at least one country.
    """
    if form.cleaned_data["countries"]:
        if form.cleaned_data["country_include"] == "Yes":
            exclusive_games = Game.objects.filter(
                Q(gameplatform__in=gp)
                & Q(gameplatform__gameplatformcountry__country__in=form.cleaned_data["countries"]),
            )

            return gp.filter(game__in=exclusive_games)
        # If platform_include is "No"
        exclusive_games = Game.objects.filter(
            Q(gameplatform__in=gp) & ~Q(gameplatform__gameplatformcountry__country__in=form.cleaned_data["countries"]),
        )

        return gp.filter(game__in=exclusive_games)

    # If there are no countries nothing needs to be done
    return gp


def country_form(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    """Filter the queryset using the country parameters.

    Args:
    ----
        form: The form that was submitted.
        gp: The queryset to use for filtering.

    Returns:
    -------
        A queryset using the country parameters.
    """
    if form.cleaned_data["country_search_type"] == "And":
        return country_form_and(form, gp)
    if form.cleaned_data["country_search_type"] == "Or":
        return country_form_or(form, gp)
    if form.cleaned_data["country_search_type"] == "Exclusive":
        return country_form_exclusive(form, gp)

    msg = f"Unknown country_search_type {form.cleaned_data['country_search_type']}"
    raise ValueError(msg)


def form_parser(formset: BaseFormSet, search_type: str) -> QuerySet[Game]:
    """Parse the forms and return a queryset of games.

    Args:
    ----
        formset: The formset that was submitted.
        search_type: The type of search to perform.

    Returns:
    -------
        The fully filtered queryset of games.
    """
    the_set: set[int] = set()
    games = Game.objects.none()

    if search_type == "And Search" and (the_set := and_form_parser(formset, the_set)):
        games = Game.objects.filter(id__in=the_set)

    if search_type == "Or Search" and (the_set := or_form_parser(formset, the_set)):
        games = Game.objects.filter(id__in=the_set)

    return (
        games.prefetch_related("gameplatform_set__platform", "gameplatform_set__gameplatformcountry_set__country")
        .distinct()
        .order_by("name")
    )


def and_form_parser(formset: BaseFormSet, intersection_set: set[int]) -> set[int]:
    """Parse the forms in and style and return a queryset of games.

    Args:
    ----
        formset: The formset that was submitted.
        intersection_set: The set to use for intersection.

    Returns:
    -------
        The fully filtered set of games.
    """
    for form in formset:
        # Check if form is valid
        if form.is_valid():
            gp = GamePlatform.objects.all()

            if form.cleaned_data.get("platforms"):
                gp = platform_form(form, gp)
            if form.cleaned_data.get("countries"):
                gp = country_form(form, gp)

                # Get all game.id values in gp
            game_ids = gp.values_list("game__id", flat=True)
            intersection_set = intersection_set.intersection(set(game_ids)) if intersection_set else set(game_ids)
    return intersection_set


def or_form_parser(formset: BaseFormSet, union_set: set[int]) -> set[int]:
    """Parse the forms in or style and return a queryset of games.

    Args:
    ----
        formset: The formset that was submitted.
        union_set: The set to use for union.

    Returns:
    -------
        The fully filtered set of games.
    """
    for form in formset:
        # Check if form is valid
        if form.is_valid():
            gp = GamePlatform.objects

            if form.cleaned_data.get("platforms"):
                gp = platform_form(form, gp)
            if form.cleaned_data.get("countries"):
                gp = country_form(form, gp)

                # Get all game.id values in gp
            game_ids = gp.values_list("game__id", flat=True)
            union_set = union_set.union(set(game_ids))
    return union_set
