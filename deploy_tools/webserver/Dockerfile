FROM alpine:3.10

COPY requirements.txt /tmp
RUN apk update \
    && apk upgrade \
    && apk add --no-cache \
        # Compilation tools
        gcc \
        musl-dev \
        jpeg \
        jpeg-dev \
        libffi \
        libffi-dev \
        # Python and scripting
        bash \
        python3 \
        python3-dev \
        # Database support
        mariadb-dev \
    && ln -s $(which python3) $(dirname $(which python3))/python \
    && python3 -m pip install \
        --no-cache-dir \
        -r /tmp/requirements.txt \
#
# Cleanup
    && rm /tmp/requirements.txt \
    && apk del \
        gcc \
        musl-dev \
        jpeg-dev \
        libffi-dev \
        python3-dev

# Add the webserver files (assets, templates, paths, etc.)
ENV SITE_DIRECTORY=/var/www \
    SERVER_USER=www-data
RUN mkdir -p ${SITE_DIRECTORY}

# Add the .env file
COPY .env "${SITE_DIRECTORY}/.env"

# Add a user to run the server
RUN addgroup ${SERVER_USER} \
    && adduser -D -s /bin/false -H -G ${SERVER_USER} ${SERVER_USER} \
    && chown -R ${SERVER_USER}:${SERVER_USER} ${SITE_DIRECTORY}

ADD lawliet ${SITE_DIRECTORY}

WORKDIR ${SITE_DIRECTORY}
COPY deploy_tools/webserver/run.sh .
CMD [ "./run.sh" ]
