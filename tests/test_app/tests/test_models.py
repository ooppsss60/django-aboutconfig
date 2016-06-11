from django.test import TestCase

try:
    from unittest.mock import patch
except:
    from mock import patch

from aboutconfig.models import DataType, Config
from aboutconfig.serializers import BoolSerializer


class DataTypeTest(TestCase):
    @patch('aboutconfig.utils.load_serializer')
    def test_get_class(self, load_serializer):
        load_serializer.return_value = BoolSerializer

        dt = DataType.objects.create(name='foo', serializer_class='foo')
        klass = dt.get_class()

        self.assertIs(klass, BoolSerializer)
        load_serializer.assert_called_once_with('foo')


class ConfigTest(TestCase):
    def setUp(self):
        self.dt = DataType.objects.get(name='String')
        self.config = config = Config.objects.create(key='foo', value='bar', data_type=self.dt,
                                       default_value='baz')

    def test_get_raw_value(self):
        self.assertEqual(self.config.get_raw_value(), 'bar')

        self.config.value = ''
        self.config.save()

        self.assertEqual(self.config.get_raw_value(), '')

        self.config.value = None
        self.config.save()

        self.assertEqual(self.config.get_raw_value(), 'baz')


    @patch('aboutconfig.utils.load_serializer')
    def test_get_value(self, load_serializer):
        load_serializer.return_value.return_value.unserialize.return_value = 'a'

        self.assertEqual(self.config.get_value(), 'a')

        load_serializer.return_value.assert_called_once_with(self.config)
        load_serializer.return_value.return_value.unserialize.assert_called_once_with('bar')


    @patch('aboutconfig.utils.load_serializer')
    def test_set_value(self, load_serializer):
        load_serializer.return_value.return_value.serialize.return_value = 'a'

        self.config.set_value('moo')
        self.assertEqual(self.config.value, 'a')
        self.assertEqual(self.config.default_value, 'baz')

        load_serializer.return_value.assert_called_once_with(self.config)
        load_serializer.return_value.return_value.serialize.assert_called_once_with('moo')


