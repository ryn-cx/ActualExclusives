"""Form for the games app."""
from django import forms
from django.forms import formset_factory

from games.models import Country, Platform


class SelectForm(forms.Form):
    """Form for selecting platforms and countries."""

    YES_NO_CHOICES = (
        ("Yes", "Yes"),
        ("No", "No"),
    )
    AND_OR_CHOICES = (
        ("Exclusive", "Exclusive"),
        ("Or", "Or"),
        ("And", "And"),
    )

    platforms = forms.ModelMultipleChoiceField(queryset=Platform.objects.all().order_by("name"), required=False)
    platform_include = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    platform_search_type = forms.ChoiceField(choices=AND_OR_CHOICES, required=False)

    countries = forms.ModelMultipleChoiceField(queryset=Country.objects.all().order_by("name"), required=False)
    country_include = forms.ChoiceField(choices=YES_NO_CHOICES, required=False)
    country_search_type = forms.ChoiceField(choices=AND_OR_CHOICES, required=False)


# Need to make this into a formset to make it possible to have multiple forms that are combined together
SelectFormSet = formset_factory(SelectForm, extra=1)
