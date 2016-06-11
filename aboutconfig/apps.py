from django.apps import AppConfig
from django.conf import settings
from django.core.cache import caches

from . import utils


def _set(key, default):
    key = 'ABOUTCONFIG_%s' % key
    setattr(settings, key, getattr(settings, key, default))


class AboutconfigConfig(AppConfig):
    name = 'aboutconfig'

    @staticmethod
    def ready():
        _set('CACHE_NAME', 'default')
        _set('CACHE_TTL', None)

        utils.preload_cache()
