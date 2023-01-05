#!/bin/bash
# MySQL8
while ! nc -z db 3306 ; do
    echo "Waiting for the MySQL service to be deployed."
    sleep 3
done
echo "MySQL service has been deployed. "

ENV_PATH=.env.prod python3 manage.py collectstatic --noinput \
    && echo "Static file collection is complete." \
    && ENV_PATH=.env.prod python3 manage.py makemigrations \
    && ENV_PATH=.env.prod python3 manage.py migrate \
    && echo "Data migration complete." \
    && ENV_PATH=.env.prod daphne -b 0.0.0.0 -p 8000 --access-log logs/access-daphne.log sugar.asgi:application
