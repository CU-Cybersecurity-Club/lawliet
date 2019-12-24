#!/bin/bash

# Set up static files
python3 manage.py collectstatic \
    --link \
    --noinput

# Set up database. We attempt to connect to the database
# multiple times, until either the connection is succesful
# or we exceed the maximum number of attempts.
for ii in {1..5}
do
    python3 manage.py makemigrations \
        && python3 manage.py migrate --run-syncdb

    RESULT=$?
    if [ $RESULT -eq 0 ]
    then
        echo "Migration succeeded. Starting webserver..."
        break
    else
        echo "Migration failed. Reattempting migration..." >&2
        sleep 5
    fi
done

if [ ! $RESULT -eq 0 ]
then
    echo <<- EOECHO
Migration failed maximum number of times. Exiting now...
EOECHO
    exit 1
fi

# Run nginx
mkdir -p /data/nginx/cache
nginx

# Run webserver
gunicorn lawliet.wsgi \
    --bind 0.0.0.0:8000 \
    --workers 2
