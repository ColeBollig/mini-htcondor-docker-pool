#!/bin/bash

# Spawn SSH daemon
/usr/sbin/sshd -D &

# Sync in anything the user dropped in the optional copy-in mount
rm -rf "/home/$USER_NAME/copy"
mkdir -p "/home/$USER_NAME/copy"
if [[ -n "$(ls -A /mnt/copy-in 2>/dev/null)" ]]; then
    cp -r /mnt/copy-in/. "/home/$USER_NAME/copy/"
fi
chown -R "$USER_NAME:$USER_NAME" "/home/$USER_NAME/copy"

# Wait for Schedd to be up on AP host
until sshpass -p $USER_PASSWORD ssh -o StrictHostKeyChecking=no $USER_NAME@$AP_HOSTNAME condor_ping; do
    echo "Waiting for Access Point accessible via SSH"
    sleep 2
done

# Fetch token for remote submission from this host
sshpass -p $USER_PASSWORD ssh -o StrictHostKeyChecking=no $USER_NAME@$AP_HOSTNAME condor_token_fetch > /home/$USER_NAME/.condor/tokens.d/ap-token
chown $USER_NAME /home/$USER_NAME/.condor/tokens.d/ap-token
chgrp $USER_NAME /home/$USER_NAME/.condor/tokens.d/ap-token
chmod 600 /home/$USER_NAME/.condor/tokens.d/ap-token

# Entrypoint sleep forever
sleep infinity
