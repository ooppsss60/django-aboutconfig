Configuration Options
==============================================

Some configuration options are provided for you to tinker with.


``ABOUTCONFIG_CACHE_NAME``
""""""""""""""""""""""""""

Configured cache's alias to use for storing the data. The alias refers to the ones used in the
Django config.

**Default value**: ``'default'``


``ABOUTCONFIG_CACHE_TTL``
"""""""""""""""""""""""""

How long the configured data should stay in cache (seconds). This value is passed directly to
Django's caching mechanism, so that means a value of ``None`` is equal to indefinite TTL.

**Default value**: ``None``


``ABOUTCONFIG_AUTOLOAD``
""""""""""""""""""""""""

Whether to automatically load the data up into cache on start-up or not. You may want to disable
this if you only want data to be loaded into cache on demand.

**Default value**: ``True``
