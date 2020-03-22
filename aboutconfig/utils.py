"""Common utilities used by the module."""

import importlib
from typing import TYPE_CHECKING, Any, NamedTuple, Optional, Type, Union, overload

from django.conf import settings
from django.core.cache import caches
from django.core.cache.backends.base import BaseCache
from django.core.exceptions import ValidationError

from .constants import CACHE_KEY_PREFIX
from .serializers import BaseSerializer


if TYPE_CHECKING:
    from typing_extensions import Literal

    from .models import Config


_SENTINEL = object()


class DataTuple(NamedTuple):
    """
    Data coming from cache.

    Optional representation when you're not sure if you stored
    a None in the cache, or nothing is found.
    """

    value: Any
    allow_template_use: bool


def _cache_key_transform(key: str) -> str:
    """Transforms the configuration key to avoid undesired collisions in cache."""

    return CACHE_KEY_PREFIX + key.lower()


def _get_cache() -> BaseCache:
    """Return the configured cache backend."""

    return caches[settings.ABOUTCONFIG_CACHE_NAME]


def _set_cache(config: "Config") -> None:
    """Put the given configuration data into cache."""

    cache = _get_cache()
    cache_key = _cache_key_transform(config.key)
    cache.set(
        cache_key,
        DataTuple(config.get_value(), config.allow_template_use),
        settings.ABOUTCONFIG_CACHE_TTL,
    )


def _delete_cache(config: "Config") -> None:
    """Remove value from cache."""

    cache = _get_cache()
    cache_key = _cache_key_transform(config.key)
    cache.delete(cache_key)


def load_class(class_path: str) -> Type:
    """Load class from absolute class path."""

    split_path = class_path.split(".")
    class_name = split_path.pop()
    module_path = ".".join(split_path)

    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def load_serializer(class_path: str) -> Type[BaseSerializer]:
    """Load a class by name/path that implements the serialization interface.

    Returns an instance of the class or raises ImportError/ValueError/AttributeError."""

    klass = load_class(class_path)

    if not BaseSerializer.is_class_valid(klass):
        raise ValueError('"{}" is not a valid serializer'.format(class_path))

    return klass


def serializer_validator(class_path: str) -> None:
    """Check whether the given class (via path) is a valid serialzier or not.

    Raises ValidationError if not valid."""

    try:
        load_serializer(class_path)
    except (ValueError, ImportError, AttributeError):
        raise ValidationError("Invalid serializer class")


# pylint: disable=missing-function-docstring
@overload
def get_config(key: str, value_only: "Literal[True]") -> Optional[Any]:
    ...


@overload
def get_config(key: str, value_only: "Literal[False]") -> DataTuple:
    ...


@overload
def get_config(key: str, value_only: bool) -> Union[DataTuple, Optional[Any]]:
    ...


def get_config(key: str, value_only: bool = True) -> Union[DataTuple, Optional[Any]]:
    """
    Get the configuration value for the given key.

    By default this function only returns the value, set value_only=False to get a
    2-tuple with the following elements: (value, allow_template_use). This functionality
    is almost certainly not needed by end-users, only included for the built-in template
    tag filtering functionality.

    Returns None if no such configuration exists (or (None, True) if value_only=False).
    """

    from .models import Config  # pylint: disable=import-outside-toplevel,cyclic-import

    cache = _get_cache()
    cache_key = _cache_key_transform(key)
    data = cache.get(cache_key, _SENTINEL)

    if data is _SENTINEL:
        try:
            config = Config.objects.select_related("data_type").get(key=key.lower())
        except Config.DoesNotExist:
            data = DataTuple(None, True)
            cache.set(cache_key, data, settings.ABOUTCONFIG_CACHE_TTL)
        else:
            data = DataTuple(config.get_value(), config.allow_template_use)
            _set_cache(config)

    return data.value if value_only else data


def preload_cache() -> None:
    """Load all configuration data into cache."""

    from .models import Config  # pylint: disable=import-outside-toplevel,cyclic-import

    for config in Config.objects.all():
        _set_cache(config)
