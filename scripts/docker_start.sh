#!/usr/bin/env bash

memcached -u nobody -d
python3 /code/tests/manage.py migrate
python3 /code/tests/manage.py runserver 0.0.0.0:80
