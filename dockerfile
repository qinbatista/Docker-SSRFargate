FROM alpine:3.18.2

ARG aws_key
ARG aws_secret

ARG google_key
ARG google_secret

ARG DISCORD_TOKEN
ARG CHATGPT_API_KEY

ARG rsa
ARG rsa_public
COPY . /

#add v2ray
WORKDIR /tmp
ARG TARGETPLATFORM
ARG TAG

COPY v2ray.sh "${WORKDIR}"/v2ray.sh
RUN set -ex \
    && apk add --no-cache ca-certificates \
    && mkdir -p /etc/v2ray /usr/local/share/v2ray /var/log/v2ray \
    # forward request and error logs to docker log collector
    && ln -sf /dev/stdout /var/log/v2ray/access.log \
    && ln -sf /dev/stderr /var/log/v2ray/error.log \
    && chmod +x "${WORKDIR}"/v2ray.sh \
    && "${WORKDIR}"/v2ray.sh "${TARGETPLATFORM}" "${TAG}"
RUN mv -f /v2ray.json /etc/v2ray/config.json

#install caddy
RUN apk add caddy
RUN mv -f /Caddyfile /etc/caddy/Caddyfile
WORKDIR /

#add discord setting
RUN echo "DISCORD_TOKEN = ${DISCORD_TOKEN}" >> /DiscordChatGPT/.env
RUN echo "CHATGPT_API_KEY = ${CHATGPT_API_KEY}" >> /DiscordChatGPT/.env

#install python3 packages
RUN apk update && apk add python3 py3-pip
RUN python3 -m pip install --upgrade pip && python3 -m pip install wheel
RUN python3 --version && pip3 --version

#install python3 packages
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirement

#install packages
RUN apk add bash make gcc unzip curl whois ffmpeg rsync sudo git tar build-base openssh aria2 screen vim wget curl proxychains-ng

#install SSR
# RUN chmod 777 ssr-install.sh
# RUN bash ssr-install.sh
# RUN cp ssr.json /etc/ssr.json

#write RSA key
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
RUN apk add aws-cli
RUN aws configure set aws_access_key_id ${aws_key}
RUN aws configure set aws_secret_access_key ${aws_secret}
RUN aws configure set default.region us-west-2
RUN aws configure set region us-west-2 --profile testing
RUN echo ${google_key} > google_key.txt
RUN echo ${google_secret} > google_secret.txt
RUN echo ${aws_key} > aws_key.txt
RUN echo ${aws_secret} > aws_secret.txt

#7171 for CN server listenning, 7031 for http, 8000 for V2ray
EXPOSE 7171/udp 7031/tcp 443/tcp

#folder for download
VOLUME [ "/download"]

WORKDIR /root
RUN apk add supervisor
RUN echo "[supervisord]" > /etc/supervisord.conf \
    && echo "nodaemon=true" >> /etc/supervisord.conf \
    && echo "[program:ssrf]" >> /etc/supervisord.conf \
    && echo "command=python3 /SSRFargate.py" >> /etc/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisord.conf"]