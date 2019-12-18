FROM nginx:alpine

###
### Add certbot
###
RUN apk update \
    && apk add --no-cache certbot openssl \
    && mkdir /root/.config

COPY /certbot-config/cli.ini /root/.config/cli.ini

# Add a cron job that renews the certificates (if necessary) every week
COPY renew-certificates.sh /usr/bin/renew-certificates
RUN ln -s /usr/bin/renew-certificates /etc/periodic/weekly

###
### Configure nginx
###
# Copy config files into the container
ADD nginx-config/ /etc/nginx

RUN \
# Create directory to store cached files in
    mkdir -p /data/nginx/cache \
# User to run the webserver
    && adduser -D -s /bin/false -H -G www-data www-data

EXPOSE 80 443

VOLUME /etc/letsencrypt

ENV SITE_SERVER=webserver \
    REDIRECT_HTTP_TO_HTTPS="no"

COPY run.sh /run.sh
CMD [ "/run.sh" ]
