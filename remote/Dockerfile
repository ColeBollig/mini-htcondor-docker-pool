FROM almalinux/9-base

# Grab environment variables for set up
ARG AP_HOSTNAME
ARG CM_HOSTNAME
ARG USER_PASSWORD
ARG USER_NAME

# Install needed/useful packages
RUN dnf update -y
RUN dnf install -y nano openssh-server openssh-clients sudo procps sshpass

# Set up SSH daemon (spawned in boot.sh)
RUN mkdir -p /var/run/sshd
RUN ssh-keygen -A
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Set up python3
RUN dnf install -y python3 python3-pip
RUN pip3 install htcondor

# Create user (give passwordless sudo)
RUN useradd -m $USER_NAME --shell /bin/bash && usermod -aG wheel $USER_NAME && echo "$USER_NAME:$USER_PASSWORD" | chpasswd
RUN echo '%wheel ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Swtich to user and cd to home directory
USER $USER_NAME
WORKDIR /home/$USER_NAME

# Set up user condor environment for remote submission
RUN mkdir -p ~/.condor/tokens.d
RUN mkdir -p ~/.condor/config

# Copy over custom user configuration file
COPY user.conf .condor/config/condor_config
RUN echo 'export CONDOR_CONFIG=~/.condor/config/condor_config' >> ~/.bashrc

# Swtich back to root
USER root
WORKDIR /

# Get boot entrypoint
COPY boot.sh /boot.sh

# Set necessary environment variables for boot
ENV USER_NAME $USER_NAME
ENV USER_PASSWORD $USER_PASSWORD
ENV AP_HOSTNAME $AP_HOSTNAME
ENV CM_HOSTNAME $CM_HOSTNAME

ENTRYPOINT [ "/boot.sh" ]
