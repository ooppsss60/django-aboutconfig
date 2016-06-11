Django-Aboutconfig
==================

**In Development**

[![Alt text](https://codeship.com/projects/49cf7540-11ab-0134-4d7f-228fbb5b3c99/status?branch=default)](https://codeship.com/projects/157317) [![codecov](https://codecov.io/bb/impala/django-aboutconfig/branch/default/graph/badge.svg)](https://codecov.io/bb/impala/django-aboutconfig)


A firefox-like about:config implementation for one-off settings in Django apps.

#### Compatible Python versions
2.7, 3.3-3.5

#### Compatible Django versions
1.9, 1.10


## Installation

You can install `aboutconfig` either from source or via pip:

    pip install django-aboutconfig

The only thing you need to do to configure it is add it to your `INSTALLED_APPS` like all other
django applications:

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        ...
        'aboutconfig'
    ]

Then just run `manage.py migrate` and you're good to go.

**Note:** `aboutconfig` relies on having a good caching mechanism to be fast (all configured values
are preloaded into cache on start-up). You should ideally have something like memcached
configured to avoid slowdowns. [See Django documentation for details](https://docs.djangoproject.com/en/stable/topics/cache/).


## Usage

By default, `aboutconfig` comes with four supported data-types: integer, boolean, string and
decimal. All data types are configurable and you can add your own if necesessary.

To add some configuration values, head over to the django admin and add an instance of the `Config`
model.

Having done this, you can access the configuration value via `aboutconfig.get_config()` in Python
code or the `get_config` template filter (load `config` before using).

### Python code:

    from aboutconfig import get_config

    def my_view(request):
        # some code...
        admin_email = get_config('admin.details.email')
        # some more code...


### Template code:

    {% load config %}

    The website admin's email is {{ 'admin.details.email'|get_config }}.


## Todo

Things that still need to be implemented:

* proper value validation when editing configs via a form
* updating of cached values via signals when models are changed