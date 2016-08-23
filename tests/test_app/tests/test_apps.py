from unittest import TestCase

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.conf import settings
from django.test import override_settings

from aboutconfig.apps import AboutconfigConfig


class AboutconfigConfigTest(TestCase):
    @patch.object(AboutconfigConfig, 'migrations_applied')
    @patch('aboutconfig.utils.preload_cache')
    def test_run_load(self, preload_cache, migrations_applied):
        del settings.ABOUTCONFIG_CACHE_NAME
        del settings.ABOUTCONFIG_CACHE_TTL
        migrations_applied.return_value = True

        AboutconfigConfig.ready()

        self.assertEqual(settings.ABOUTCONFIG_CACHE_NAME, 'default')
        self.assertIsNone(settings.ABOUTCONFIG_CACHE_TTL)
        preload_cache.assert_called_once_with()


    @patch.object(AboutconfigConfig, 'migrations_applied')
    @patch('aboutconfig.utils.preload_cache')
    @override_settings(ABOUTCONFIG_AUTOLOAD=False)
    def test_run_load_disabled(self, preload_cache, migrations_applied):
        del settings.ABOUTCONFIG_CACHE_NAME
        del settings.ABOUTCONFIG_CACHE_TTL
        migrations_applied.return_value = True

        AboutconfigConfig.ready()

        self.assertEqual(settings.ABOUTCONFIG_CACHE_NAME, 'default')
        self.assertIsNone(settings.ABOUTCONFIG_CACHE_TTL)
        preload_cache.assert_not_called()


    @patch.object(AboutconfigConfig, 'migrations_applied')
    @patch('aboutconfig.utils.preload_cache')
    def test_run_load_not_ready(self, preload_cache, migrations_applied):
        del settings.ABOUTCONFIG_CACHE_NAME
        del settings.ABOUTCONFIG_CACHE_TTL
        migrations_applied.return_value = False

        AboutconfigConfig.ready()

        self.assertEqual(settings.ABOUTCONFIG_CACHE_NAME, 'default')
        self.assertIsNone(settings.ABOUTCONFIG_CACHE_TTL)
        preload_cache.assert_not_called()
