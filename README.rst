Django-Aboutconfig
==================

|License: GPL v3| |CI| |codecov| |PyPI version| |Openhub|

A firefox-like about:config implementation for one-off settings in
Django apps.

Compatible Python versions
^^^^^^^^^^^^^^^^^^^^^^^^^^

3.6+

Compatible Django versions
^^^^^^^^^^^^^^^^^^^^^^^^^^

2.0 - 3.0

Installation
------------

You can install ``aboutconfig`` either from source or via pip:

.. code-block:: sh

    pip install django-aboutconfig

The only thing you need to do to configure it is add it to your
``INSTALLED_APPS`` like all other django applications:

.. code-block:: python

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        ...
        'aboutconfig',
    ]

Then just run ``manage.py migrate`` and you're good to go.

**Note:** ``aboutconfig`` relies on having a good caching mechanism to
be fast (all configured values are preloaded into cache on start-up).
You should ideally have something like memcached configured to avoid
slowdowns. `See Django documentation for
details <https://docs.djangoproject.com/en/stable/topics/cache/>`__.

Usage
-----

By default, ``aboutconfig`` comes with four supported data-types:
integer, boolean, string and decimal. All data types are configurable
and you can add your own if necesessary.

To add some configuration values, head over to the django admin and add
an instance of the ``Config`` model.

Having done this, you can access the configuration value via
``aboutconfig.get_config()`` in Python code or the ``get_config``
template filter (load ``config`` before using).

Python code:
~~~~~~~~~~~~

.. code-block:: python

    from aboutconfig import get_config

    def my_view(request):
        # some code...
        admin_email = get_config('admin.details.email')
        # some more code...

Template code:
~~~~~~~~~~~~~~

.. code-block:: django

    {% load config %}

    The website admin's email is {{ 'admin.details.email'|get_config }}.

    >>> An assignment tag also exists for convenience:

    {% get_config 'admin.details.email' as email %}
    The website admin's email is <a href="mailto:{{ email }}">{{ email }}</a>.

.. |License: GPL v3| image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
   :target: http://www.gnu.org/licenses/gpl-3.0
.. |CI| image:: https://img.shields.io/gitlab/pipeline/impala1/django-aboutconfig
   :target: https://gitlab.com/impala1/django-aboutconfig/pipelines
.. |codecov| image:: https://codecov.io/gl/impala1/django-aboutconfig/branch/master/graph/badge.svg
   :target: https://codecov.io/gl/impala1/django-aboutconfig
.. |PyPI version| image:: https://badge.fury.io/py/django-aboutconfig.svg
   :target: https://pypi.python.org/pypi/django-aboutconfig
.. |Openhub| image:: https://www.openhub.net/p/django-aboutconfig/widgets/project_thin_badge.gif
   :target: https://www.openhub.net/p/django-aboutconfig
