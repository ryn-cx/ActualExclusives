"""This module modifies environmental variables so that Django models can be accessed outside of Django itself.

When using this module to be imported before any Django models are imported. With it being located in the root directory
and starting with an underscore isort should automatically make it import before any Django models.

I hate how sketchy this is, but it is the easiest solution for consistently setting up Django with minimal issues from
linters"""

from __future__ import annotations

import os

import django
from extended_path import ExtendedPath

file_name = ExtendedPath(__file__).parent.name
os.environ["DJANGO_SETTINGS_MODULE"] = f"{file_name}.settings"
django.setup()
