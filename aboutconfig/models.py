from collections import OrderedDict

from django.db import models
from django.core.validators import RegexValidator
from django.utils.encoding import python_2_unicode_compatible

from .constants import KEY_REGEX
from . import utils


@python_2_unicode_compatible
class DataType(models.Model):
    name = models.CharField(max_length=32)
    serializer_class = models.CharField(max_length=256, validators=[utils.serializer_validator])

    def get_class(self):
        return utils.load_serializer(self.serializer_class)


    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Config(models.Model):
    key = models.CharField(max_length=512, validators=[RegexValidator(KEY_REGEX)])
    value = models.CharField(max_length=1024, blank=True, null=True)
    data_type = models.ForeignKey(DataType, related_name='+')
    default_value = models.CharField(max_length=1024, editable=False)
    allow_template_use = models.BooleanField(default=True)


    def save(self, **kwargs):
        self.key = self.key.lower()
        super(Config, self).save(**kwargs)


    def get_raw_value(self):
        """Get serialized value.

        Tries to get manually set value before falling back to default value."""

        if self.value is None:
            return self.default_value
        else:
            return self.value


    def get_value(self):
        """Get unserialized value."""

        return self._get_serializer().unserialize(self.get_raw_value())


    def set_value(self, val):
        self.value = self._get_serializer().serialize(val)


    def _get_serializer(self):
        return self.data_type.get_class()(self)


    def in_cache(self):
        return utils.get_config(self.key) is not None
    in_cache.boolean = True # django admin icon fix


    def __str__(self):
        return '{}={}'.format(self.key, self.get_raw_value())
