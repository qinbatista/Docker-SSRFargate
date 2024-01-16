FROM python:3.8.13-alpine3.16 as python

COPY . /
RUN pip3 install --upgrade pip
#[Start] V2ray--------------------------------------------------
WORKDIR /tmp

#all variables are on github action
ARG V2RAY_CADDY_CONFIG
ARG V2RAY_CADDYFILE
ARG V2RAY_DOWNLOADURL
ARG V2RAY_TARGETPLATFORM
ARG V2RAY_TAG

RUN ls /Docker-V2rayServer
RUN pwd

#install v2ray
COPY /Docker-V2rayServer/v2ray.sh "${WORKDIR}"/v2ray.sh
RUN set -ex \
    && apk add --no-cache ca-certificates \
    && mkdir -p /etc/v2ray /usr/local/share/v2ray /var/log/v2ray \
    # forward request and error logs to docker log collector
    && ln -sf /dev/stdout /var/log/v2ray/access.log \
    && ln -sf /dev/stderr /var/log/v2ray/error.log \
    && chmod +x "${WORKDIR}"/v2ray.sh \
    && "${WORKDIR}"/v2ray.sh "${V2RAY_TARGETPLATFORM}" "${V2RAY_TAG}" "${V2RAY_DOWNLOADURL}"

RUN apk add wget
RUN wget ${V2RAY_CADDYFILE}
RUN wget ${V2RAY_CADDY_CONFIG}
RUN mv -f ./v2rayconfig.json /etc/v2ray/config.json

#install caddy
RUN apk add caddy
RUN mv -f ./Caddyfile /etc/caddy/Caddyfile

#remove all folder
RUN rm -rf /tmp
#[End] V2ray-----------------------------------------------------


#[Start] GoogleDDNS--------------------------------------------------

ARG GOOGLE_USERNAME_V6
ARG GOOGLE_PASSWORD_V6
ARG DOMAIN_NAME_V6
ARG GOOGLE_USERNAME_V4
ARG GOOGLE_PASSWORD_V4
ARG DOMAIN_NAME_V4

RUN echo ${GOOGLE_USERNAME_V6} > /GOOGLE_USERNAME_V6
RUN echo ${GOOGLE_PASSWORD_V6} > /GOOGLE_PASSWORD_V6
RUN echo ${DOMAIN_NAME_V6} > /DOMAIN_NAME_V6
RUN echo ${GOOGLE_USERNAME_V4} > /GOOGLE_USERNAME_V4
RUN echo ${GOOGLE_PASSWORD_V4} > /GOOGLE_PASSWORD_V4
RUN echo ${DOMAIN_NAME_V4} > /DOMAIN_NAME_V4
RUN pip3 install -r /Docker-GoogleDDNSClient/requirements.txt
#[End] GoogleDDNS-----------------------------------------------------

#[Start] HTTPHelper--------------------------------------------------
RUN pip install -r /Docker-HTTPHelper/requirements.txt
#[End] HTTPHelper--------------------------------------------------

#add discord setting
ARG DISCORD_TOKEN
ARG CHATGPT_API_KEY
RUN echo "DISCORD_TOKEN = ${DISCORD_TOKEN}" >> /DiscordChatGPT/.env
RUN echo "CHATGPT_API_KEY = ${CHATGPT_API_KEY}" >> /DiscordChatGPT/.env

#install python3 packages
# RUN apk update && apk add python3.8 py3-pip
# RUN python3 -m pip install --upgrade pip && python3 -m pip install wheel
# RUN python3 --version && pip3 --version

#install packages
RUN apk add bash make gcc unzip curl whois ffmpeg rsync sudo git tar build-base openssh aria2 screen vim wget curl proxychains-ng

#write RSA key
ARG rsa
ARG rsa_public
RUN echo -----BEGIN OPENSSH PRIVATE KEY----- >> id_rsa
RUN echo ${rsa} >> id_rsa
RUN echo -----END OPENSSH PRIVATE KEY----- >> id_rsa
RUN echo ${rsa_public} > id_rsa.pub

#for config NAS
RUN mkdir ~/.ssh/
RUN touch ~/.ssh/authorized_keys
RUN touch ~/.ssh/known_hosts
RUN mv ./id_rsa ~/.ssh/
RUN mv ./id_rsa.pub ~/.ssh/
RUN chmod 600 ~/.ssh/id_rsa

# config github download
RUN ssh-keyscan -t rsa github.com > ~/.ssh/known_hosts

#install AWS CLI
ARG aws_key
ARG aws_secret
RUN apk add aws-cli
RUN aws configure set aws_access_key_id ${aws_key}
RUN aws configure set aws_secret_access_key ${aws_secret}
RUN aws configure set default.region us-west-2
RUN aws configure set region us-west-2 --profile testing


WORKDIR /
RUN apk add supervisor
RUN echo "[supervisord]" > /etc/supervisord.conf \
    && echo "nodaemon=true" >> /etc/supervisord.conf \
    # && echo "[program:ssrf]" >> /etc/supervisord.conf \
    # && echo "command=python3 /SSRFargate.py" >> /etc/supervisord.conf \
    && echo "[program:googleddns]" >> /etc/supervisord.conf \
    && echo "command=python3  /Docker-GoogleDDNSClient/GoogleDDNSClient.py" >> /etc/supervisord.conf \
    && echo "[program:caddy]" >> /etc/supervisord.conf \
    && echo "command=caddy run --config /etc/caddy/Caddyfile" >> /etc/supervisord.conf \
    && echo "[program:v2ray]" >> /etc/supervisord.conf \
    && echo "command=v2ray run -c /etc/v2ray/config.json" >> /etc/supervisord.conf\
    && echo "[program:httphelper]" >> /etc/supervisord.conf \
    && echo "command=python3 /Docker-HTTPHelper/HTTPHelper.py" >> /etc/supervisord.conf

#7171 for CN server listenning, 7031 for http, 443 for V2ray
EXPOSE 7171/udp 7031/tcp 443/tcp
CMD ["supervisord", "-c", "/etc/supervisord.conf"]