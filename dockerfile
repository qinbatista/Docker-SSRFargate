FROM debian:10-slim
ADD * ./
RUN apt-get clean
RUN apt-get update
RUN apt-get -y install make gcc python3 unzip python3-pip curl

#install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN aws configure set aws_access_key_id AKIA4ARPVTO2AUQ3FLNL
RUN aws configure set aws_secret_access_key 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
RUN aws configure set default.region us-west-2
RUN aws configure set region us-west-2 --profile testing

#install python3 packages
ADD requirements.txt /
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

#install SSR
RUN chmod 777 ssr-install.sh
RUN bash ssr-install.sh
RUN cp ssr.json /etc/ssr.json

#7000-7030 for SSR, 7171 for CN server listenning
EXPOSE 7000-7030/tcp 7171/udp
WORKDIR /root
CMD  ["python","/SSRFargate.py"]