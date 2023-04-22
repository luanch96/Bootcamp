FROM nginx:stable

# Configuration files and data output folder
VOLUME /hidden
WORKDIR /hidden

# Base packages
RUN apt-get update && \
    apt-get -y install \
    tor torsocks ntpdate \
    qrencode \
    openssh-server

# Some custom stuff
COPY files/motd /etc/motd

# Ssh
RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo -u 1000 user 
RUN  echo 'user:user' | chpasswd
COPY sshd_config /etc/ssh/sshd_config
COPY files/authorized_keys /home/ubuntu/.ssh/authorized_keys
RUN service ssh start
EXPOSE 22


# Tor Config
ADD ./torrc /etc/tor/torrc

# Nginx configuration 
COPY ./hidden/ /usr/share/nginx/html/
COPY ./nginx.conf /etc/nginx/conf.d/nginx.conf
EXPOSE 80

# Entrypoint copy
COPY files/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
