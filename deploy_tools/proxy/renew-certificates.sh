#!/bin/sh

create_self_signed_certificates() {
    if [ ! -d /etc/letsencrypt/self-signed/$1 ]
    then
        mkdir -p /etc/letsencrypt/self-signed/$1
        openssl req \
            -x509 \
            -newkey rsa:4096 \
            -keyout /etc/letsencrypt/self-signed/$1/$1.key \
            -out /etc/letsencrypt/self-signed/$1/$1.cert \
            -nodes \
            -subj "/CN=$1" \
            -days 7
    fi
}

echo -e "[$(date)] Running certbot...\n"

if [ $DEVELOPMENT -eq 0 ]
then
    # Renew any certificates that are close to expiring
    certbot renew

    # If no certificates exist yet, then create some
    certbot certonly \
        --agree-tos \
        --non-interactive \
        -c ${HOME}/.config/cli.ini \
        --domains $SERVER_NAME,www.$SERVER_NAME \
        --keep-until-expiring
fi

# If certbot failed, create some self-signed certificates instead
if [ ! -f /etc/letsencrypt/live/$SERVER_NAME/fullchain.pem ]
then
    echo "Unable to create certificate with certbot. Creating self-signed certificates..."
    create_self_signed_certificates $SERVER_NAME
fi
