from unittest import TestCase
import six

from aboutconfig.constants import KEY_REGEX

class KeyRegexTest(TestCase):
    def test_run(self):
        assertRegex = self.assertRegex if six.PY3 else self.assertRegexpMatches
        assertNotRegex = self.assertNotRegex if six.PY3 else self.assertNotRegexpMatches

        assertRegex('a', KEY_REGEX)
        assertRegex('a.b', KEY_REGEX)
        assertRegex('aa.bbb.CCC.1.2.3._', KEY_REGEX)
        assertNotRegex('', KEY_REGEX)
        assertNotRegex('.', KEY_REGEX)
        assertNotRegex('a.', KEY_REGEX)
        assertNotRegex(' ', KEY_REGEX)
        assertNotRegex(' a.b', KEY_REGEX)
