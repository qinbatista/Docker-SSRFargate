FROM debian:10-slim
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
RUN aws configure set aws_access_key_id AKIA4ARPVTO2IWF2IYPL
RUN aws configure set aws_secret_access_key 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
RUN aws configure set default.region us-west-2
RUN aws configure set region us-west-2 --profile testing

#install SSR
RUN chmod 777 ssr-install.sh
RUN bash ssr-install.sh
RUN cp ssr.json /etc/ssr.json

#7000-7030 for SSR, 7171 for CN server listenning
EXPOSE 7000-7030/tcp 7171/udp
WORKDIR /root
CMD  ["python","/SSRFargate.py"]