#!/bin/bash
while ! nc -z db 3306 ; do
    echo "Waiting for the MySQL service to be deployed."
    sleep 3
done
echo "MySQL service has been deployed."

while ! nc -z mq 5672 ; do
    echo "Waiting for the rabbitmq service to be deployed."
    sleep 3
done
echo "rabbitmq service has been deployed."

while ! nc -z cache 6379 ; do
    echo "Waiting for the redis service to be deployed."
    sleep 3
done
echo "redis service has been deployed."



ENV_PATH=.env.prod python3 manage.py collectstatic --noinput \
    && echo "Static file collection is completed." \
    && ENV_PATH=.env.prod python3 manage.py makemigrations \
    && ENV_PATH=.env.prod python3 manage.py migrate \
    && echo "MySQL data migration is completed." \
    && ENV_PATH=.env.prod supervisord -c celery_app.conf \
    && echo "celery service has been deployed." \
    && ENV_PATH=.env.prod daphne -b 0.0.0.0 -p 8000 --access-log logs/access-daphne.log sugar.asgi:application
