# -*- coding: utf-8 -*-

import os

from setuptools import find_packages, setup

from aboutconfig import __version__


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_STRING = ".".join(str(s) for s in __version__)

with open(os.path.join(BASE_DIR, "README.rst")) as fp:
    long_description = fp.read()

setup(
    name="django-aboutconfig",
    version=VERSION_STRING,
    url="https://gitlab.com/impala1/django-aboutconfig",
    license="GPLv3+",
    description="A firefox-like about:config implementation for one-off settings in Django apps.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    keywords=["django", "library", "configuration"],
    author="Kirill Stepanov",
    author_email="mail@kirillstepanov.me",
    packages=find_packages(),
    download_url=(
        "https://gitlab.com/impala1/django-aboutconfig/-/archive/{version}/"
        "django-aboutconfig-{version}.tar.gz".format(version=VERSION_STRING)
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=["Django>=2.0",],
    python_requires=">=3.6",
    include_package_data=True,
    zip_safe=False,
)
