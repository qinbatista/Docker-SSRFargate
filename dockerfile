FROM debian:10-slim

ARG aws_key
ARG aws_secret

ARG google_key
ARG google_secret

ARG rsa
ARG rsa_public

#install packages
RUN ls
COPY . /
WORKDIR /DiscordChatGPT
RUN ls

RUN apt-get clean
RUN apt-get update
RUN apt-get -y install make gcc python3 unzip python3-pip curl whois ffmpeg rsync python3-distutils sudo git tar build-essential ssh aria2 screen vim wget curl proxychains locales


#install SSR
RUN chmod 777 ssr-install.sh
RUN bash ssr-install.sh
RUN cp ssr.json /etc/ssr.json

#install python3 packages
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirement

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
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN aws configure set aws_access_key_id ${aws_key}
RUN aws configure set aws_secret_access_key ${aws_secret}
RUN aws configure set default.region us-west-2
RUN aws configure set region us-west-2 --profile testing
RUN echo ${google_key} > google_key.txt
RUN echo ${google_secret} > google_secret.txt
RUN echo ${aws_key} > aws_key.txt
RUN echo ${aws_secret} > aws_secret.txt



#7000-7030 for SSR, 7171 for CN server listenning
EXPOSE 7000-7031/tcp 7171/udp

#folder for download
VOLUME [ "/download"]

WORKDIR /root
CMD  ["python3","/SSRFargate.py"]