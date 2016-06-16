from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

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
        self.config = Config.objects.create(key='foo', value='bar', data_type=self.dt,
                                            default_value='baz')

    def test_get_raw_value(self):
        self.assertEqual(self.config.get_raw_value(), 'bar')

        self.config.value = ''
        self.config.save()

        self.assertEqual(self.config.get_raw_value(), 'baz')

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


    @patch('aboutconfig.utils.get_config')
    def test_in_cache_true(self, get_config):
        get_config.return_value = 'x'
        self.assertTrue(self.config.in_cache())
        get_config.assert_called_once_with(self.config.key)


    @patch('aboutconfig.utils.get_config')
    def test_in_cache_true(self, get_config):
        get_config.return_value = None
        self.assertFalse(self.config.in_cache())
        get_config.assert_called_once_with(self.config.key)


    def test_key_lowers(self):
        self.config.key = 'Yo'
        self.config.save()
        self.assertEqual(self.config.key, 'yo')


    def test_key_uniqueness(self):
        with self.assertRaisesRegexp(IntegrityError, 'key'):
            Config.objects.create(key='foo', value='3', data_type=self.dt)


    @patch.object(Config, '_get_serializer')
    def test_full_clean_fail(self, get_serializer):
        get_serializer.return_value.validate.side_effect = ValidationError('foo')

        with self.assertRaisesRegexp(ValidationError, 'foo'):
            self.config.full_clean()

        get_serializer.assert_called_once_with()
        get_serializer.return_value.validate.assert_called_once_with('bar')


    @patch.object(Config, '_get_serializer')
    def test_full_clean_success(self, get_serializer):
        self.config.full_clean()
        get_serializer.assert_called_once_with()
        get_serializer.return_value.validate.assert_called_once_with('bar')


    @patch('aboutconfig.utils._set_cache')
    def test_post_save_signal(self, set_cache):
        self.config.save()
        set_cache.assert_called_once_with(self.config)


    @patch.object(Config, '_get_serializer')
    def test_revert_to_default(self, get_serializer):
        self.config.value = ''
        self.config.full_clean()

        self.assertEqual(self.config.get_raw_value(), 'baz')
        self.assertIsNone(self.config.value)
        self.assertSequenceEqual(
            get_serializer.return_value.validate.call_args_list, [], 'validate() was called')


    @patch.object(Config, '_get_serializer')
    def test_no_val_no_default_error(self, get_serializer):
        self.config.value = None
        self.config.default_value = None

        with self.assertRaisesRegexp(ValidationError, 'value'):
            self.config.full_clean()


    def test_key_namespace(self):
        self.config.key = 'ggg'
        self.config.save()

        self.assertEqual(self.config.key_namespace, 'ggg')

        self.config.key = 'abc.def.ghi.jkl'
        self.config.save()

        self.assertEqual(self.config.key_namespace, 'abc')
