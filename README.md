
# SSRFargate
## What it is?
This is a docker source code of SSR based on open encryption connection. More info about [SSR](https://github.com/shadowsocksrr/shadowsocksr). The docker can be deployed on AWS->ECS->Fargata container which is the cheapest docker container right now, around $2/month.\


```
docker run -itdv /home/admin/download:/download -p 7031:7031 -p 8000:8000 -p 443 qinbatista/ssrfargateqin
```

## How to use it?

1: Build this docker and push this docker into your docker repository (*qinbatista* is my docker repository)

```
docker build -t qinbatista/ssrfargate .
```
2: Create a task definition on AWS->ECS and set this docker for the task.

3: Launch the Docker by AWS->ECS->Services

4: Connect the SSR by the client, the configuration setting from the client should be like this except for the *server*, change the *YourDockerIP* to your own docker IP like 111.123.234.345.

```
{
	"enable" : true,
	"password" : "qwer1234",
	"method" : "chacha20",
	"server" : "YourDockerIP",
	"obfs" : "http_simple",
	"obfs_param" : "",
	"protocol" : "auth_sha1_v4",
	"protocol_param" : "",
	"server_port" : 7000,
	"local_port": 1126
  }
```

## Advanced usage

#### Set Docker action
Push this project to your GitHub repository, and add SSRFargateDockerLogin into setting->Environments
Your SSRFargateDockerLogin should contain:

- AWS ECS Fargate permission

>AWS_ACCESS

>AWS_KEY

- Docker push permission

>DOCKERHUB_TOKEN

>DOCKERHUB_USERNAME

- Google DDNS permission

>GOOGLE_KEY

>GOOGLE_SECRET

Once you push this project, the docker action will build this image and push it to docker, then the Git Action will close the Fargate Container from AWS ECS, but your AWS ECS services will always open a new docker, so your new docker image will be pulled to the AWS ECS task.

## Check if IP is banned from other regions.
- The SSRFargate will open a 7171 port to receive messages from other regions.
- If you want to test if this region is able to use the server, send a UPD message like `1.1.1.1,0` the `1.1.1.1` means target IP, and the `0` means you connect successfully (`1` means connect failed).
- Your testing server should consist of trying to connect the SSRFargate.
- once the testing server sent 3 times to connect failed, the target server will close itself, but ECS->services will open a new one with new IP, then you just wait for the GoogleDDNS to refresh your IP.

## Change SSR Configurations

Check the `ssr.json` in this repository

- Default ports are `7000-7030`,

- The default password is `qwer1234`,

- Default encryptions are:

 `"method":"chacha20"`

 `"protocol":"auth_chain_b"`

 `"obfs":"tls1.2_ticket_auth",`

More encryptions from [here](https://github.com/shadowsocksrr/shadowsocks-rss/blob/master/ssr.md), each of them has its own advantage and disadvantage. Default encryption chooses the safest encryption.

## Check Docker health
- the port 7031 is opened for HTTP accessing

