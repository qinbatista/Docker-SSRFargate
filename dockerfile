FROM python:3.8.13-alpine3.16 as python

COPY . /
RUN pip3 install --upgrade pip

#[Start] V2ray--------------------------------------------------
WORKDIR /tmp
#all variables are on github action
ARG V2RAY_ADDRESS
ARG V2RAY_DOWNLOADURL
ARG V2RAY_TARGETPLATFORM
ARG V2RAY_TAG
ENV V2RAY_ADDRESS=${V2RAY_ADDRESS}
#install v2ray config
RUN apk add wget
RUN wget ${V2RAY_DOWNLOADURL}/${V2RAY_ADDRESS}/v2rayconfig.json

RUN cat /tmp/v2rayconfig.json
#install v2ray
COPY /Docker-V2rayServer/v2ray.sh "${WORKDIR}"/v2ray.sh
RUN set -ex \
    && apk add --no-cache ca-certificates \
    && mkdir -p /etc/v2ray /usr/local/share/v2ray /var/log/v2ray \
    && ln -sf /dev/stdout /var/log/v2ray/access.log \
    && ln -sf /dev/stderr /var/log/v2ray/error.log \
    && chmod +x "${WORKDIR}"/v2ray.sh \
    && "${WORKDIR}"/v2ray.sh "${V2RAY_TARGETPLATFORM}" "${V2RAY_TAG}" "${V2RAY_DOWNLOADURL}"
#install caddy
RUN apk add caddy
RUN wget ${V2RAY_DOWNLOADURL}/${V2RAY_ADDRESS}/Caddyfile
RUN cat /tmp/Caddyfile
RUN mv -f /tmp/Caddyfile /etc/caddy/Caddyfile
RUN pip install -r /Docker-V2rayServer/requirements.txt
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
RUN apk add --update curl
#[End] GoogleDDNS-----------------------------------------------------

#[Start] HTTPHelper--------------------------------------------------
RUN apk add --update curl
RUN pip install -r /Docker-HTTPHelper/requirements.txt
#[End] HTTPHelper--------------------------------------------------


#[Start] Docker-CNListener--------------------------------------------------
RUN apk add --update curl
RUN pip install -r /Docker-HTTPHelper/requirements.txt
#[End] Docker-CNListener--------------------------------------------------


#[Start] CNListener--------------------------------------------------
RUN pip3 install --upgrade pip
RUN pip3 install -r /Docker-CNListener/requirements.txt
ARG aws_key
ARG aws_secret

RUN apk add aws-cli
RUN aws configure set aws_access_key_id ${aws_key}
RUN aws configure set aws_secret_access_key ${aws_secret}
RUN aws configure set default.region us-west-2
RUN aws configure set region us-west-2 --profile testing

RUN apk add curl
#[End] CNListener--------------------------------------------------

WORKDIR /
RUN apk add supervisor
RUN echo "[supervisord]" > /etc/supervisord.conf \
    && echo "nodaemon=true" >> /etc/supervisord.conf \
    #CN listener
    && echo "[program:cn_listener]" >> /etc/supervisord.conf \
    && echo "command=python3 /Docker-CNListener/CNListener.py" >> /etc/supervisord.conf \
    #google ddns
    && echo "[program:googleddns]" >> /etc/supervisord.conf \
    && echo "command=python3  /Docker-GoogleDDNSClient/GoogleDDNSClient.py" >> /etc/supervisord.conf \
    #v2ray
    && echo "[program:caddy-python]" >> /etc/supervisord.conf \
    && echo "command=python3 /Docker-V2rayServer/CaddyLauncher.py" >> /etc/supervisord.conf \
    && echo "[program:v2ray]" >> /etc/supervisord.conf \
    && echo "command=v2ray run -c /etc/v2ray/config.json" >> /etc/supervisord.conf\
    #http helper
    && echo "[program:httphelper]" >> /etc/supervisord.conf \
    && echo "command=python3 /Docker-HTTPHelper/HTTPHelper.py" >> /etc/supervisord.conf

#7171 for CN server listenning, 7031 for http, 443 for V2ray
EXPOSE 7171/udp 7001/tcp 443/tcp
CMD ["supervisord", "-c", "/etc/supervisord.conf"]