import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.test import TestCase as DatabaseTestCase, override_settings

from aboutconfig.constants import CACHE_KEY_PREFIX
from aboutconfig.models import Config, DataType
from aboutconfig.serializers import IntSerializer
from aboutconfig.utils import (
    DataTuple,
    _cache_key_transform,
    _get_cache,
    get_config,
    load_serializer,
    preload_cache,
    serializer_validator,
)


MEMCACHED_HOST = os.environ.get("MEMCACHED_HOST", "127.0.0.1:11211")


class LoadSerializerTest(TestCase):
    def test_sucess(self):
        self.assertIs(load_serializer("aboutconfig.serializers.IntSerializer"), IntSerializer)

    def test_failure_not_serializer(self):
        with self.assertRaises(ValueError):
            load_serializer("collections.namedtuple")

    def test_invalid_class(self):
        with self.assertRaises(ImportError):
            load_serializer("foo.bar")

        with self.assertRaises(ValueError):
            load_serializer("foo")

        with self.assertRaises(AttributeError):
            load_serializer("collections.a")


class SerializerValidatorTest(TestCase):
    def test_success(self):
        serializer_validator("aboutconfig.serializers.IntSerializer")
        self.assertTrue(True)  # no-op

    def test_failure(self):
        with self.assertRaises(ValidationError):
            serializer_validator("collections.namedtuple")

        with self.assertRaises(ValidationError):
            serializer_validator("foo.bar")

        with self.assertRaises(ValidationError):
            serializer_validator("foo")

        with self.assertRaises(ValidationError):
            serializer_validator("collections.a")


class CacheKeyTransformTest(TestCase):
    def test_run(self):
        self.assertEqual(_cache_key_transform("x"), CACHE_KEY_PREFIX + "x")
        self.assertEqual(_cache_key_transform("XxX"), CACHE_KEY_PREFIX + "xxx")


class GetCacheTest(TestCase):
    @override_settings(
        ABOUTCONFIG_CACHE_NAME="foo",
        CACHES={
            "foo": {
                "BACKEND": "django.core.cache.backends.db.DatabaseCache",
                "LOCATION": "my_cache_table",
            },
            "bar": {
                "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
                "LOCATION": "/var/tmp/django_cache",
            },
        },
    )
    def test_run(self):
        from django.core.cache.backends.db import DatabaseCache

        self.assertIsInstance(_get_cache(), DatabaseCache)


@override_settings(
    ABOUTCONFIG_CACHE_NAME="default",
    ABOUTCONFIG_CACHE_TTL=None,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": MEMCACHED_HOST,
        }
    },
)
class GetConfigTest(DatabaseTestCase):
    def setUp(self):
        int_dt = DataType.objects.get(name="Integer")
        config = Config(key="USER.AGE", data_type=int_dt)
        config.set_value(42)
        config.save()
        _get_cache().clear()  # undo signal cache update

    def tearDown(self):
        _get_cache().clear()

    def test_no_such_key(self):
        self.assertIsNone(get_config("foo.bar"))
        self.assertEqual(get_config("foo.bar", False), DataTuple(None, True))
        self.assertEqual(get_config("foo.bar", False), DataTuple(None, True))

    def test_key_exists(self):
        self.assertEqual(get_config("User.Age"), 42)
        self.assertEqual(get_config("USER.AGE"), 42)
        self.assertEqual(get_config("USER.AGE", False), DataTuple(42, True))

    def test_num_queries(self):
        with self.assertNumQueries(1):
            get_config("user.age")

        with self.assertNumQueries(0):
            get_config("user.age")


@override_settings(
    ABOUTCONFIG_CACHE_NAME="default",
    ABOUTCONFIG_CACHE_TTL=12345,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": MEMCACHED_HOST,
        }
    },
)
class PreloadCacheTest(DatabaseTestCase):
    def setUp(self):
        int_dt = DataType.objects.get(name="Integer")
        config = Config(key="USER.AGE", data_type=int_dt)
        config.set_value(42)
        config.save()

    def tearDown(self):
        _get_cache().clear()

    def test_run(self):
        cache = _get_cache()
        cache.clear()  # save signal automatically sets the cache
        key = _cache_key_transform("user.age")

        self.assertFalse(cache.has_key(key))
        preload_cache()
        self.assertTrue(cache.has_key(key))
        self.assertEqual(cache.get(key), DataTuple(42, True))


class DeleteCacheTest(DatabaseTestCase):
    def setUp(self):
        int_dt = DataType.objects.get(name="Integer")
        self.config = Config(key="USER.AGE", data_type=int_dt)
        self.config.set_value(42)
        self.config.save()

    def tearDown(self):
        _get_cache().clear()

    def test_delete(self):
        key = _cache_key_transform("user.age")

        self.assertEqual(_get_cache().get(key), DataTuple(42, True))
        self.config.delete()
        self.assertIsNone(_get_cache().get(key))
