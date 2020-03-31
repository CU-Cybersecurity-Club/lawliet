#!/bin/sh

###
### This script installs some extensions for Guacamole
###
EXT_URL="http://apache.org/dyn/closer.cgi?action=download&filename=guacamole/${GUACAMOLE_VERSION}/binary/"

# Download extensions
exts="\
guacamole-auth-quickconnect\
"

echo "${exts}" \
| xargs -I {} \
    wget "${EXT_URL}/{}-${GUACAMOLE_VERSION}.tar.gz" \
        --progress=bar:force \
        --follow-ftp \
        --no-verbose \
        -O "/tmp/{}-${GUACAMOLE_VERSION}.tar.gz"

# Move all extensions into the GUACAMOLE_HOME directory
mkdir -p "${GUACAMOLE_HOME}/extensions"

find /tmp \
    -mindepth 1 \
    -maxdepth 1 \
    -type f \
    -name "*-${GUACAMOLE_VERSION}.tar.gz" \
    -exec tar xvf "{}" \
        -C /tmp \
        --exclude "*/*/*" \
        --wildcards \
        --no-anchored "*-${GUACAMOLE_VERSION}.jar" \;

find /tmp \
    -mindepth 2 \
    -maxdepth 2 \
    -type f \
    -name "*-${GUACAMOLE_VERSION}.jar" \
    -exec mv "{}" "${GUACAMOLE_HOME}/extensions" \;

# Cleanup
find /tmp \
    -mindepth 1 \
    -maxdepth 1 \
    -name "*-${GUACAMOLE_VERSION}*" \
    -exec rm -rf "{}" \;
