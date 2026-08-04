#!/bin/bash

# Start SSH daemon
/usr/sbin/sshd -D &

# Start condor (from inherited HTCondor docker image)
exec /start.sh


