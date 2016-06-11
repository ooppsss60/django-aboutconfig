import six
from decimal import Decimal

class BaseSerializer(object):
    def __init__(self, config):
        self.config = config

    @staticmethod
    def is_class_valid(klass):
        try:
            assert hasattr(klass, 'serialize')
            assert hasattr(klass, 'unserialize')
        except AssertionError:
            return False
        else:
            return True

    def serialize(self, val):
        raise NotImplementedError()

    def unserialize(self, val):
        raise NotImplementedError()


class StrSerializer(BaseSerializer):
    def serialize(self, val):
        return six.text_type(val)

    def unserialize(self, val):
        return six.text_type(val)


class IntSerializer(BaseSerializer):
    def serialize(self, val):
        return six.text_type(val)

    def unserialize(self, val):
        return int(val)


class BoolSerializer(BaseSerializer):
    def serialize(self, val):
        return 'true' if val else 'false'

    def unserialize(self, val):
        return val == 'true'


class DecimalSerializer(BaseSerializer):
    def serialize(self, val):
        return six.text_type(val)

    def unserialize(self, val):
        return Decimal(val)
