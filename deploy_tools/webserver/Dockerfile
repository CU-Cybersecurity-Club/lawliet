FROM nginx:alpine

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

# Add a user to run the server
RUN adduser -D -s /bin/false -H -G www-data www-data \
    && mkdir -p /var/www/src \
    && chown -R www-data:www-data /var/www

VOLUME /var/www/src

#
# Configure Nginx
#
COPY deploy_tools/webserver/nginx-config /etc/nginx

WORKDIR /var/www/src
COPY deploy_tools/webserver/run.sh /
CMD [ "/run.sh" ]
