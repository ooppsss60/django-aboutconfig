from unittest import TestCase

from aboutconfig.constants import KEY_REGEX


class KeyRegexTest(TestCase):
    def test_run(self):
        self.assertRegex("a", KEY_REGEX)
        self.assertRegex("a.b", KEY_REGEX)
        self.assertRegex("aa.bbb.CCC.1.2.3._", KEY_REGEX)
        self.assertNotRegex("", KEY_REGEX)
        self.assertNotRegex(".", KEY_REGEX)
        self.assertNotRegex("a.", KEY_REGEX)
        self.assertNotRegex(" ", KEY_REGEX)
        self.assertNotRegex(" a.b", KEY_REGEX)
