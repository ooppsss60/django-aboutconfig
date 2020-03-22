from unittest import TestCase
from unittest.mock import patch

from django.core.management import call_command


class ConfigCacheWarmTest(TestCase):
    @patch("aboutconfig.utils.preload_cache")
    def test_run(self, preload_cache):
        call_command("config_warm_cache")
        preload_cache.assert_called_once()
