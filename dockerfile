FROM debian:10-slim

ARG aws_key
ARG aws_secret

ARG google_key
ARG google_secret

ADD * /
RUN ls
RUN apt-get clean
RUN apt-get update
RUN apt-get -y install make gcc python3 unzip python3-pip curl

#install python3 packages
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirement

#install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN aws configure set aws_access_key_id aws_key
RUN aws configure set aws_secret_access_key aws_secret
RUN aws configure set default.region us-west-2
RUN aws configure set region us-west-2 --profile testing
RUN echo ${google_key} > google_key.txt
RUN echo ${google_secret} > google_secret.txt
#install SSR
RUN chmod 777 ssr-install.sh
RUN bash ssr-install.sh
RUN cp ssr.json /etc/ssr.json

#7000-7030 for SSR, 7171 for CN server listenning
EXPOSE 7000-7031/tcp 7171/udp
WORKDIR /root
CMD  ["python3","/SSRFargate.py"]