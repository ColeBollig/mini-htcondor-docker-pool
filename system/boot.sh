#!/bin/bash

# Start SSH daemon
/usr/sbin/sshd -D &

# Sync in anything the user dropped in the optional copy-in mount
rm -rf "/home/$USER_NAME/copy"
mkdir -p "/home/$USER_NAME/copy"
if [[ -n "$(ls -A /mnt/copy-in 2>/dev/null)" ]]; then
    cp -r /mnt/copy-in/. "/home/$USER_NAME/copy/"
fi
chown -R "$USER_NAME:$USER_NAME" "/home/$USER_NAME/copy"

# Start condor (from inherited HTCondor docker image)
exec /start.sh


