import datetime
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from games.forms import SelectFormSet
from games.functions import form_parser


@csrf_exempt
def index(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        formset = SelectFormSet(request.GET)
        if not formset.is_valid():
            formset = SelectFormSet()
    else:
        formset = SelectFormSet()
    return render(request, "games/index.html", {"formset": formset})


@csrf_exempt
def games(request: HttpRequest) -> HttpResponse:
    start = datetime.datetime.now()
    # Manage invalid forms
    formset = SelectFormSet(request.GET)
    search_type = request.GET.get("search_type")

    if not formset.is_valid():
        return HttpResponse("Invalid Form")

    if not search_type:
        return HttpResponse("Invalid Form")

    # Truncate results to 1,000 to avoid overloading the web browser
    games = form_parser(formset, search_type)[:1000]

    # TODO: Do all of this inside of the Django template instead of passing in JSON
    output5: dict[int, Any] = {}
    for game in games:
        output5[game.id] = {
            "name": game.name,
            "platforms": {},
            "description": game.description,
            "image": game.image,
        }
        for platform in game.gameplatform_set.all():
            output5[game.id]["platforms"][platform.platform.name] = []
            for region in platform.gameplatformcountry_set.all():
                output5[game.id]["platforms"][platform.platform.name] += [region.country.flag]

    context_data = {"games": output5, "start": start}
    output = render(request, "games/results.html", context_data)
    return output
