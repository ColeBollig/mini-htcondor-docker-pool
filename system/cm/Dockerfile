FROM htcondor/cm:latest

# Get environment defined variables for set up
ARG AP_HOSTNAME
ARG EP_HOSTNAME
ARG SIGNING_SECRET
ARG USER_PASSWORD
ARG USER_NAME

# Install required/desired packages
RUN dnf	update -y
RUN dnf	install	-y nano openssh-server openssh-clients sudo procps

# Set up SSH daemon (spawned in boot.h)
RUN mkdir -p /var/run/sshd
RUN ssh-keygen -A
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Create user (with passwordless sudo)
RUN useradd -m $USER_NAME --shell /bin/bash && usermod -aG wheel $USER_NAME && echo "$USER_NAME:$USER_PASSWORD" | chpasswd
RUN echo '%wheel ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Create pool password/signing key
RUN condor_store_cred add -c -p	$SIGNING_SECRET

# Add configuration to allow daemonss to advertise to the pool
RUN echo "ALLOW_ADVERTISE_MASTER = \$(ALLOW_ADVERTISE_MASTER) $AP_HOSTNAME $EP_HOSTNAME" > /etc/condor/config.d/99_advertise_pool.conf
RUN echo "ALLOW_ADVERTISE_SCHEDD = \$(ALLOW_ADVERTISE_SCHEDD) $AP_HOSTNAME" >> /etc/condor/config.d/99_advertise_pool.conf
RUN echo "ALLOW_ADVERTISE_STARTD = \$(ALLOW_ADVERTISE_STARTD) $EP_HOSTNAME" >> /etc/condor/config.d/99_advertise_pool.conf

# Copy custom configuration
COPY config/ /etc/condor/config.d/

# Get boot entrypoint
COPY boot.sh /boot.sh

# Set necessary environment variables for boot
ENV USER_NAME $USER_NAME

ENTRYPOINT [ "/boot.sh" ]
