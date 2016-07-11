"""
Template tags and filters provided by the module.

Add "{% load config %}" in your templates to access.
"""

from django import template
from django.template.defaultfilters import stringfilter

from .. import utils

# pylint: disable=invalid-name
register = template.Library()


def _get_config_for_template(key):
    """Get the configuration data while respecting the template use flag."""

    data = utils.get_config(key, value_only=False)

    if data.allow_template_use:
        return data.value
    else:
        return None


@register.filter(name='get_config')
@stringfilter
def get_config_filter(key):
    """
    Get the configuration value for the given key.

    If allow_template_use is False, will act as if the key is not set.

    Use in combination with the built-in `default` filter for default values.
    """

    return _get_config_for_template(key)


@register.assignment_tag(name='get_config')
def get_config_assignment_tag(key):
    """
    Get the configuration value for the given key.

    Assigns the value to another variable.
    """

    return _get_config_for_template(key)
