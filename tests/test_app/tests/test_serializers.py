from unittest import TestCase
from decimal import Decimal
import six

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from aboutconfig import serializers


class BaseSerializerTest(TestCase):
    klass = None

    def setUp(self):
        self.c = MagicMock()
        self.s = self.klass(self.c)


class BaseSerializerClassTest(TestCase):
    s = serializers.BaseSerializer

    def test_class_fail(self):
        noop = lambda: None
        self.assertFalse(self.s.is_class_valid(object))
        self.assertFalse(self.s.is_class_valid(type('x', (), {'serialize': noop})))
        self.assertFalse(self.s.is_class_valid(type('x', (), {'unserialize': noop})))

    def test_class_pass(self):
        noop = lambda: None
        self.assertTrue(self.s.is_class_valid(type('x', (), {
            'unserialize': noop,
            'serialize': noop
        })))


class BoolSerializerTest(BaseSerializerTest):
    klass = serializers.BoolSerializer

    def test_serialize(self):
        self.assertEqual(self.s.serialize(True), 'true')
        self.assertEqual(self.s.serialize(1), 'true')
        self.assertEqual(self.s.serialize('x'), 'true')
        self.assertEqual(self.s.serialize(False), 'false')
        self.assertEqual(self.s.serialize(0), 'false')
        self.assertEqual(self.s.serialize(''), 'false')

        self.assertIsInstance(self.s.serialize(''), six.string_types)

    def test_unserialize(self):
        self.assertIs(self.s.unserialize('true'), True)
        self.assertIs(self.s.unserialize('false'), False)

        self.assertIsInstance(self.s.unserialize('true'), bool)


class StrSerializerTest(BaseSerializerTest):
    klass = serializers.StrSerializer

    def test_serialize(self):
        self.assertEqual(self.s.serialize('abc123'), 'abc123')
        self.assertEqual(self.s.serialize('1'), '1')
        self.assertEqual(self.s.serialize(''), '')
        self.assertEqual(self.s.serialize('   '), '   ')

        self.assertIsInstance(self.s.serialize(''), six.string_types)

    def test_unserialize(self):
        self.assertEqual(self.s.unserialize('abc123'), 'abc123')
        self.assertEqual(self.s.unserialize('1'), '1')
        self.assertEqual(self.s.unserialize(''), '')
        self.assertEqual(self.s.unserialize('   '), '   ')

        self.assertIsInstance(self.s.unserialize('1'), six.string_types)


class IntSerializerTest(BaseSerializerTest):
    klass = serializers.IntSerializer

    def test_serialize(self):
        self.assertEqual(self.s.serialize(1), '1')
        self.assertEqual(self.s.serialize(0), '0')
        self.assertEqual(self.s.serialize(-1), '-1')
        self.assertEqual(self.s.serialize(1000000000000000000000), '1000000000000000000000')

        self.assertIsInstance(self.s.serialize(1), six.string_types)

    def test_unserialize(self):
        self.assertEqual(self.s.unserialize('1'), 1)
        self.assertEqual(self.s.unserialize('0'), 0)
        self.assertEqual(self.s.unserialize('-1'), -1)
        self.assertEqual(self.s.unserialize('1000000000000000000000'), 1000000000000000000000)

        self.assertIsInstance(self.s.unserialize('1'), six.integer_types)
        self.assertIsInstance(self.s.unserialize('1000000000000000000000'), six.integer_types)


class DecimalSerializerTest(BaseSerializerTest):
    klass = serializers.DecimalSerializer

    def test_serialize(self):
        self.assertEqual(self.s.serialize(Decimal(0)), '0')
        self.assertEqual(self.s.serialize(Decimal(-5)), '-5')
        self.assertEqual(self.s.serialize(Decimal('3.1415')), '3.1415')

        self.assertIsInstance(self.s.serialize(Decimal(0)), six.string_types)

    def test_unserialize(self):
        self.assertEqual(self.s.unserialize('0'), Decimal(0))
        self.assertEqual(self.s.unserialize('-5'), Decimal(-5))
        self.assertEqual(self.s.unserialize('3.1415'), Decimal('3.1415'))

        self.assertIsInstance(self.s.unserialize('0'), Decimal)
