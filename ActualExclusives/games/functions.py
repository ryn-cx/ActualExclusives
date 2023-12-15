from django.db.models import Count, Q, QuerySet
from django.forms import BaseFormSet

from games.forms import SelectForm
from games.models import Country, Game, GamePlatform, Platform


def platform_form_exclusive(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    platforms = Platform.objects.exclude(id__in=form.cleaned_data["platforms"])

    # Get all games that are on this platform
    exclusive_games = Game.objects.exclude(gameplatform__platform__in=platforms)

    # Count the number of platforms each game is on
    exclusive_games = exclusive_games.annotate(counter=Count("gameplatform"))

    # Filter out games that do not have the right number of platforms
    exclusive_games = exclusive_games.filter(counter=len(form.cleaned_data["platforms"]))

    if form.cleaned_data["platform_include"] == "Yes":
        return gp.filter(game__in=exclusive_games)
    else:
        return gp.exclude(game__in=exclusive_games)


def platform_form_and(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    # Get a list of all of the games on that platform/in that region
    game = Game.objects
    for platform in form.cleaned_data["platforms"]:
        game = game.filter(gameplatform__platform=platform)

    if form.cleaned_data["platform_include"] == "Yes":
        return gp.filter(game__in=game, platform__in=form.cleaned_data["platforms"])
    else:
        return gp.exclude(game__in=game)


def platform_form_or(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    if form.cleaned_data["platform_include"] == "Yes":
        return gp.filter(platform__in=form.cleaned_data["platforms"])
    else:
        # Get a list of all of the games on that platform
        game = Game.objects.filter(gameplatform__platform__in=form.cleaned_data["platforms"])

        return gp.exclude(game__in=game)


def platform_form(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    if form.cleaned_data["platform_search_type"] == "And":
        return platform_form_and(form, gp)
    elif form.cleaned_data["platform_search_type"] == "Or":
        return platform_form_or(form, gp)
    elif form.cleaned_data["platform_search_type"] == "Exclusive":
        return platform_form_exclusive(form, gp)
    else:
        raise Exception("Unknown platform_search_type")


def country_form_and(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    for country in form.cleaned_data["countries"]:
        if form.cleaned_data["country_include"] == "Yes":
            exclusive_games = Game.objects.filter(
                Q(gameplatform__in=gp) & Q(gameplatform__gameplatformcountry__country=country)
            )

            return gp.filter(game__in=exclusive_games)
        else:
            exclusive_games = Game.objects.filter(
                Q(gameplatform__in=gp) & ~Q(gameplatform__gameplatformcountry__country=country)
            )

            gp = gp.filter(gameplatformcountry__country=country)
    return gp


def country_form_or(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    if form.cleaned_data["countries"]:
        if form.cleaned_data["country_include"] == "Yes":
            exclusive_games = Game.objects.filter(
                Q(gameplatform__in=gp)
                & Q(gameplatform__gameplatformcountry__country__in=form.cleaned_data["countries"])
            )

            return gp.filter(game__in=exclusive_games)
        else:
            exclusive_games = Game.objects.filter(
                Q(gameplatform__in=gp)
                & ~Q(gameplatform__gameplatformcountry__country__in=form.cleaned_data["countries"])
            )

            return gp.filter(game__in=exclusive_games)
    return gp


def country_form_exclusive(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    other_countries = Country.objects.exclude(id__in=form.cleaned_data["countries"])

    # Filter based on the video games
    exclusive_games = Game.objects.filter(
        Q(gameplatform__in=gp) & ~Q(gameplatform__gameplatformcountry__country__in=other_countries)
    )

    if form.cleaned_data["platform_include"] == "Yes":
        return gp.filter(game__in=exclusive_games)
    else:
        return gp.exclude(game__in=exclusive_games)


def country_form(form: SelectForm, gp: QuerySet[GamePlatform]) -> QuerySet[GamePlatform]:
    if form.cleaned_data["country_search_type"] == "And":
        return country_form_and(form, gp)
    elif form.cleaned_data["country_search_type"] == "Or":
        return country_form_or(form, gp)
    elif form.cleaned_data["country_search_type"] == "Exclusive":
        return country_form_exclusive(form, gp)
    else:
        raise Exception("Unknown country_search_type")


def form_parser(formset: BaseFormSet, search_type: str = "And Search") -> QuerySet[Game]:
    intersection_set: set[int] = set()
    union_set: set[int] = set()
    games = Game.objects.none()

    if search_type == "And Search":
        for form in formset:
            # Check if form is valid
            if form.is_valid() and form.has_changed():
                gp = GamePlatform.objects.all()

                if form.cleaned_data.get("platforms"):
                    gp = platform_form(form, gp)
                if form.cleaned_data.get("countries"):
                    gp = country_form(form, gp)

                # Get all game.id values in gp
                game_ids = gp.values_list("game__id", flat=True)
                if intersection_set:
                    intersection_set = intersection_set.intersection(set(game_ids))
                else:
                    intersection_set = set(game_ids)
        if intersection_set:
            games = Game.objects.filter(id__in=intersection_set)

    else:  # search_type == "Or Search":
        for form in formset:
            # Check if form is valid
            if form.is_valid() and form.has_changed():
                gp = GamePlatform.objects

                if form.cleaned_data.get("platforms"):
                    gp = platform_form(form, gp)
                if form.cleaned_data.get("countries"):
                    gp = country_form(form, gp)

                # Get all game.id values in gp
                game_ids = gp.values_list("game__id", flat=True)
                union_set = union_set.union(set(game_ids))

        if union_set:
            games = Game.objects.filter(id__in=union_set)

    return (
        games.prefetch_related("gameplatform_set__platform", "gameplatform_set__gameplatformcountry_set__country")
        .distinct()
        .order_by("name")
    )
