from unittest import TestCase

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.conf import settings
from django.test import override_settings

from aboutconfig.apps import AboutconfigConfig


class AboutconfigConfigTest(TestCase):
    @patch('aboutconfig.utils.preload_cache')
    def test_run(self, preload_cache):
        self.assertFalse(hasattr(settings, 'ABOUTCONFIG_CACHE_NAME'))
        self.assertFalse(hasattr(settings, 'ABOUTCONFIG_CACHE_TTL'))

        AboutconfigConfig.ready()

        self.assertEqual(settings.ABOUTCONFIG_CACHE_NAME, 'default')
        self.assertIsNone(settings.ABOUTCONFIG_CACHE_TTL)
        preload_cache.assert_called_once_with()
