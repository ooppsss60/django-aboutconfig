from unittest import TestCase
from unittest.mock import patch

from aboutconfig import get_config


class ModuleTest(TestCase):
    @patch("aboutconfig.utils.get_config")
    def test_simple(self, mock_get_config):
        mock_get_config.return_value = 123
        self.assertEqual(get_config("abc"), 123)
        mock_get_config.assert_called_once_with("abc", True)

    @patch("aboutconfig.utils.get_config")
    def test_data(self, mock_get_config):
        mock_get_config.return_value = (1, True)
        self.assertEqual(get_config("abc", False), (1, True))
        mock_get_config.assert_called_once_with("abc", False)
