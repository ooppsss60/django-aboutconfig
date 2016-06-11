import importlib

from django.core.exceptions import ValidationError
from django.core.cache import caches
from django.conf import settings

from .serializers import BaseSerializer
from .constants import CACHE_KEY_PREFIX

_SENTINEL = object()


def _cache_key_transform(key):
    return CACHE_KEY_PREFIX + key.lower()


def _get_cache():
    return caches[settings.ABOUTCONFIG_CACHE_NAME]


def load_serializer(class_path):
    split_path = class_path.split('.')
    class_name = split_path.pop()
    module_path = '.'.join(split_path)

    module = importlib.import_module(module_path)
    klass = getattr(module, class_name)

    if not BaseSerializer.is_class_valid(klass):
        raise ValueError('"{}" is not a valid serializer'.format(class_path))

    return klass


def serializer_validator(class_path):
    try:
        load_serializer(class_path)
    except (ValueError, ImportError, AttributeError):
        raise ValidationError('Invalid serializer class')


def get_config(key):
    from .models import Config

    cache = _get_cache()
    cache_key = _cache_key_transform(key)

    val = cache.get(cache_key, _SENTINEL)

    if val is _SENTINEL:
        try:
            config = Config.objects.get(key=key.lower())
        except Config.DoesNotExist:
            val = None
        else:
            val = config.get_value()

        cache.set(cache_key, val, settings.ABOUTCONFIG_CACHE_TTL)

    return val


def preload_cache():
    from .models import Config

    cache = _get_cache()

    for config in Config.objects.all():
        cache_key = _cache_key_transform(config.key)
        cache.set(cache_key, config.get_value(), settings.ABOUTCONFIG_CACHE_TTL)
