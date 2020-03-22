"""Database models used by this module."""

import json
from typing import TYPE_CHECKING, Any, Dict, Type

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.dispatch import receiver
from django.forms import TextInput
from django.forms.widgets import Widget
from django.utils.translation import ugettext_lazy as _

from . import utils
from .constants import KEY_REGEX


if TYPE_CHECKING:
    from .serializers import BaseSerializer


__all__ = ("DataType", "Config")


class DataType(models.Model):
    """
    Model representing the data type.

    Each model instance is associated with a serializer class that performs the casting
    of python objects to strings and back.
    """

    name = models.CharField(max_length=32, verbose_name=_("Name"))
    serializer_class = models.CharField(
        max_length=256,
        validators=[utils.serializer_validator],
        verbose_name=_("Serializer class"),
        help_text=_("Must be a class that implements serialize, unserialize and validate methods."),
    )
    widget_class = models.CharField(
        max_length=256,
        blank=True,
        verbose_name=_("Widget class"),
        help_text=_("Widget class used to edit values of this data type. TextInput by default."),
    )
    widget_args_raw = models.CharField(
        max_length=1024,
        default="{}",
        verbose_name=_("Raw widget arguments"),
        help_text=_("Additional data for the value field widget (JSON)."),
    )

    class Meta:
        verbose_name = _("Data-type")

    @property
    def widget_args(self) -> Dict[str, Any]:
        """Parse widget args value."""

        return json.loads(self.widget_args_raw)

    @widget_args.setter
    def widget_args(self, val: Dict[str, Any]) -> None:
        """Serialize widget args value."""

        self.widget_args_raw = json.dumps(val)

    def get_class(self) -> Type["BaseSerializer"]:
        """Load and the configured serializer class."""

        return utils.load_serializer(self.serializer_class)

    def get_widget_class(self) -> Type[Widget]:
        """Load the widget configured class."""

        if not self.widget_class:
            return TextInput

        return utils.load_class(self.widget_class)

    def __str__(self) -> str:
        return self.name


class Config(models.Model):
    """
    Model representing the user-defined configuration data.

    Most of the time just key, value and data_type need to be set. The default_value field is
    used for by 3rd-party applications that rely on this module that require that some sane value
    is set in the configuration. Users can override this if wish, but the default value remains.

    The allow_template_use field is only used in the get_config template filter. There are times
    when you have some sensitive configuration stored, but want to prevent it from potentially
    leaking out via user-configurable templates. If the value is set to false, the filter will act
    as if the configuration does not exist at all.

    Note: an empty string is equivalent to None, and the configuration will fall back to the
    default value.
    """

    EMPTY_VALUES = (None, "")

    key = models.CharField(
        max_length=512,
        validators=[RegexValidator(KEY_REGEX)],
        unique=True,
        verbose_name=_("Key"),
        help_text=_("Period separated strings. All keys are case-insensitive."),
    )
    key_namespace = models.CharField(max_length=512, db_index=True, verbose_name=_("Key namespace"))
    value = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("Value"))
    data_type = models.ForeignKey(
        DataType, related_name="+", verbose_name=_("Data-type"), on_delete=models.CASCADE
    )
    default_value = models.CharField(
        max_length=1024,
        editable=False,
        verbose_name=_("Default value"),
        help_text=_("Default value set by setting provider. Used by 3rd-party apps."),
    )
    allow_template_use = models.BooleanField(
        default=True,
        verbose_name=_("Allow template use"),
        help_text=_(
            "Prevent settings from being accessible via the template filter. Can "
            "be useful for API-keys, for example"
        ),
    )

    class Meta:
        ordering = ("key", "value", "default_value")
        verbose_name = _("Config")

    def save(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=arguments-differ
        """Save model to database."""

        self.key = self.key.lower()
        self.key_namespace = self.key.split(".")[0]
        super().save(*args, **kwargs)

    def full_clean(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=arguments-differ
        """Validate model data before saving."""

        super().full_clean(*args, **kwargs)

        if self.value in self.EMPTY_VALUES:
            self.value = None

            if self.default_value is None:
                raise ValidationError({"value": ValidationError(_("A value is required"))})

            # have default value to fall back on
            return

        try:
            self._get_serializer().validate(self.value)
        except ValidationError as e:
            raise ValidationError({"value": e})

    def get_raw_value(self) -> str:
        """
        Get serialized value.

        Tries to get manually set value before falling back to default value.
        """

        if self.value in self.EMPTY_VALUES:
            return self.default_value

        return self.value

    def get_value(self) -> Any:
        """Get unserialized value."""

        return self._get_serializer().unserialize(self.get_raw_value())

    def set_value(self, val: Any) -> None:
        """Set the configuration value via a python object. Takes care of the serialization."""

        self.value = self._get_serializer().serialize(val)

    def _get_serializer(self) -> "BaseSerializer":
        """Get the configured serializer class instance."""

        return self.data_type.get_class()(self)

    # pylint: disable=protected-access
    def in_cache(self) -> bool:
        """
        Check if the configuration value is already present in cache.

        Works like a python get_config() call - ignores allow_template_use setting.
        """

        key = utils._cache_key_transform(self.key)
        return utils._get_cache().has_key(key)

    # django admin icon fix
    in_cache.boolean = True  # type: ignore

    def __str__(self) -> str:
        return "{}={}".format(self.key, self.get_raw_value())


# pylint: disable=unused-argument
@receiver(models.signals.post_save, sender=Config)
def update_cache(instance: Config, **kwargs: Any) -> None:
    """
    Update cache for the given configuration instance.

    Automatically called on configuration creation/update.
    """

    # pylint: disable=protected-access
    utils._set_cache(instance)


# pylint: disable=unused-argument
@receiver(models.signals.post_delete, sender=Config)
def delete_cache(instance: Config, **kwargs: Any) -> None:
    """
    Remove cache for the given configuration instance.

    Automatically called on configuration deletion.
    """

    # pylint: disable=protected-access
    utils._delete_cache(instance)
