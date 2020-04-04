FROM nginx:alpine

# Initial webserver config
RUN mkdir -p /data/nginx/cache \
    && adduser -D -s /bin/false -H -G www-data www-data \
    && mkdir -p /var/www/html

ADD conf.d /etc/nginx/conf.d
ADD nginx.conf /etc/nginx/

EXPOSE 80 443
