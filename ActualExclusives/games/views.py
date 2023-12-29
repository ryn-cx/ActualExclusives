"""Views for the games app."""
from __future__ import annotations

import datetime
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from games.forms import SelectFormSet
from games.functions import form_parser


@csrf_exempt
def index(request: HttpRequest) -> HttpResponse:
    """Index page."""
    if request.method == "GET":
        formset = SelectFormSet(request.GET)
        if not formset.is_valid():
            formset = SelectFormSet()
    else:
        formset = SelectFormSet()
    return render(request, "games/index.html", {"formset": formset})


@csrf_exempt
def games(request: HttpRequest) -> HttpResponse:
    """Results page."""
    start = datetime.datetime.now().astimezone()
    # Manage invalid forms
    formset = SelectFormSet(request.GET)
    search_type = request.GET.get("search_type")

    if not formset.is_valid():
        return HttpResponse("Invalid Form")

    if not search_type:
        return HttpResponse("Invalid Form")

    # Truncate results to 1,000 to avoid people using the site as a database
    games = form_parser(formset, search_type)[:1000]

    context_data = {"games": games, "start": start}
    return render(request, "games/results.html", context_data)
