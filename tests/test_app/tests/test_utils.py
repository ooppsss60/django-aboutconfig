from unittest import TestCase

from django.core.exceptions import ValidationError

from aboutconfig.utils import load_serializer, serializer_validator
from aboutconfig.serializers import IntSerializer

class LoadSerializerTest(TestCase):
    def test_sucess(self):
        self.assertIs(load_serializer('aboutconfig.serializers.IntSerializer'), IntSerializer)

    def test_failure_not_serializer(self):
        with self.assertRaises(ValueError):
            load_serializer('collections.namedtuple')

    def test_invalid_class(self):
        with self.assertRaises(ImportError):
            load_serializer('foo.bar')

        with self.assertRaises(ValueError):
            load_serializer('foo')

        with self.assertRaises(AttributeError):
            load_serializer('collections.a')


class SerializerValidatorTest(TestCase):
    def test_success(self):
        serializer_validator('aboutconfig.serializers.IntSerializer')
        self.assertTrue(True) # no-op

    def test_failure(self):
        with self.assertRaises(ValidationError):
            serializer_validator('collections.namedtuple')

        with self.assertRaises(ValidationError):
            serializer_validator('foo.bar')

        with self.assertRaises(ValidationError):
            serializer_validator('foo')

        with self.assertRaises(ValidationError):
            serializer_validator('collections.a')
