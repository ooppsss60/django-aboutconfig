__version__ = (0, 0, 1)
default_app_config = 'aboutconfig.apps.AboutconfigConfig'


def get_config(key, value_only=True):
    """Get configured value by key.

    By default returns value only. If `value_only` is `False`, returns an instance of
    aboutconfig.utils.DataTuple which also contains the `allow_template_use` value.

    This is a lazy wrapper around `utils.get_config()`."""

    from . import utils

    return utils.get_config(key, value_only)
