#!/bin/sh

# Renew certbot certificates
renew-certificates

# Run cron daemon
crond

# Create log directory for Nginx
mkdir -p /var/log/nginx
chown -R www-data:www-data /var/log/nginx

export DOLLAR='$'
SITES_AVAILABLE=/etc/nginx/sites-available

envsubst < $SITES_AVAILABLE/default.template > $SITES_AVAILABLE/default

#
# Configure HTTPS
#
if [ ! -f /etc/letsencrypt/live/$SERVER_NAME/fullchain.pem ]
then
    export SSL_CERT=/etc/letsencrypt/self-signed/$SERVER_NAME/$SERVER_NAME.cert
    export SSL_KEY=/etc/letsencrypt/self-signed/$SERVER_NAME/$SERVER_NAME.key
else
    export SSL_CERT=/etc/letsencrypt/live/$SERVER_NAME/fullchain.pem;
    export SSL_KEY=/etc/letsencrypt/live/$SERVER_NAME/privkey.pem;
fi

envsubst < $SITES_AVAILABLE/https.template > $SITES_AVAILABLE/https

#
# Configure HTTP
#

if [ "$REDIRECT_HTTP_TO_HTTPS" = "no" ]
then
    HTTP_TEMPLATE=$SITES_AVAILABLE/http.template
elif [ "$REDIRECT_HTTP_TO_HTTPS" = "yes" || "$REDIRECT_HTTP_TO_HTTPS" = "301" ]
then

    HTTP_TEMPLATE=$SITES_AVAILABLE/http.redirect.template
    export REDIRECT_CODE="301"
elif [ "$REDIRECT_HTTP_TO_HTTPS" = "302" ]
then
    HTTP_TEMPLATE=$SITES_AVAILABLE/http.redirect.template
    export REDIRECT_CODE="302"
else
    cat <<- EOTEXT
Error: invalid option for REDIRECT_HTTP_TO_HTTPS: '$REDIRECT_HTTP_TO_HTTPS'

Available options: no, yes, 301, 302
EOTEXT
    exit 1
fi

envsubst < $HTTP_TEMPLATE > $SITES_AVAILABLE/http

#
# Start nginx. Restart whenever the server dies
#

while [ 1 ]
do
    nginx -g 'daemon off;'

    if [ ! $? -eq 0 ]
    then
        echo "Restarting Nginx proxy in a few seconds..."
        sleep 5
    fi
done
