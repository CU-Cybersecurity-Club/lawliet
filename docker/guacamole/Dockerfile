FROM guacamole/guacamole:latest

ARG GUACAMOLE_VERSION=1.1.0
ENV GUACAMOLE_HOME=/etc/guacamole

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p "${GUACAMOLE_HOME}/extensions"
COPY add_extensions.sh /tmp
RUN /tmp/add_extensions.sh \
    && rm /tmp/add_extensions.sh
