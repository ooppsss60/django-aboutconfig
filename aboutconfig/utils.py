import importlib

from django.core.exceptions import ValidationError

from .serializers import BaseSerializer

def load_serializer(class_path):
    split_path = class_path.split('.')
    class_name = split_path.pop()
    module_path = '.'.join(split_path)

    module = importlib.import_module(module_path)
    klass = getattr(module, class_name)

    if not BaseSerializer.is_class_valid(klass):
        raise ValueError('"{}" is not a valid serializer'.format(class_path))

    return klass


def serializer_validator(class_path):
    try:
        load_serializer(class_path)
    except (ValueError, ImportError, AttributeError):
        raise ValidationError('Invalid serializer class')
