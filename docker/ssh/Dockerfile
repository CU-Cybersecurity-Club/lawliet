ARG FROM_IMAGE
FROM "${FROM_IMAGE}"

# Install OpenSSH
RUN apt-get update \
    && apt-get install -y \
        openssh-server \
#
# Cleanup
    && rm -rf /var/lib/apt/lists/*

# Add a new user who will be able to SSH into
# the machine.
RUN useradd \
        --shell $(which bash) \
        --create-home \
        --base-dir /home \
        lawliet \
#
# Set the user's password to "lawliet"
    && echo "lawliet:lawliet" | chpasswd

# Customize the SSH configuration
COPY sshd_config /etc/ssh/sshd_config

# Set additional configuration options
ENV TERM=xterm-256color

# Run the SSH server on boot
COPY run.sh /
CMD [ "/run.sh" ]
