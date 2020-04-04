#!/bin/sh
touch /var/log/auth.log
service ssh start
tail -f /var/log/auth.log
