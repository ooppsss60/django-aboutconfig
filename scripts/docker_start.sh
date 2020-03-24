#!/usr/bin/env bash

set -e

python3 /code/tests/manage.py migrate

cat <<EOF | python3 /code/tests/manage.py shell
import os
from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.exists():
    User.objects.create_superuser(
        os.environ.get("SUPERUSER_USERNAME", "root"),
        "root@example.com",
        os.environ.get("SUPERUSER_PASSWORD", "root"),
    )
    print("Created superuser")
EOF

python3 /code/tests/manage.py runserver 0.0.0.0:80
