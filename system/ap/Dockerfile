FROM htcondor/submit:latest

# Get environment defined variables for set up
ARG CM_HOSTNAME
ARG REMOTE_HOSTNAME
ARG SIGNING_SECRET
ARG USER_PASSWORD
ARG USER_NAME

# Install needed/desired packages
RUN dnf	update -y
RUN dnf	install	-y nano openssh-server openssh-clients sudo procps

# Set up SSH daemon (spawned in boot.sh)
RUN mkdir -p /var/run/sshd
RUN ssh-keygen -A
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Set up token authentication
RUN echo "TRUST_DOMAIN = $CM_HOSTNAME" > /etc/condor/config.d/99_trust_domain.conf
RUN condor_store_cred add -c -p $SIGNING_SECRET
RUN condor_token_create -identity condor@$CM_HOSTNAME -token pool-idtoken
RUN rm $(condor_config_val SEC_PASSWORD_FILE)

# Set up token signing key for remote submission
RUN dd if=/dev/urandom of=$(condor_config_val SEC_PASSWORD_DIRECTORY)/remote-signing-key bs=64 count=1
RUN chmod 400 $(condor_config_val SEC_PASSWORD_DIRECTORY)/remote-signing-key

RUN echo "SEC_TOKEN_ISSUER_KEY = remote-signing-key" > /etc/condor/config.d/99_remote_submission.conf 
RUN echo "SEC_TOKEN_FETCH_ALLOWED_SIGNING_KEYS = remote-signing-key" >> /etc/condor/config.d/99_remote_submission.conf
RUN echo "ALLOW_WRITE = \$(ALLOW_WRITE) $REMOTE_HOSTNAME" >> /etc/condor/config.d/99_remote_submission.conf

# Copy custom configuration
COPY config/ /etc/condor/config.d/

# Create user
RUN useradd -m $USER_NAME --shell /bin/bash && usermod -aG wheel $USER_NAME && echo "$USER_NAME:$USER_PASSWORD" | chpasswd
RUN echo '%wheel ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Copy boot entrypoint
COPY boot.sh /boot.sh
ENTRYPOINT [ "/boot.sh" ]
