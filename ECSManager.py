# -*- coding: utf-8 -*-
import subprocess
import uuid
import os
import json
from socket import *
import platform


class ECSManager:
    def __init__(self):

        if platform.system() == "Darwin":
            self.__file_path = "/Users/qin/Desktop/logs.txt"
            self.__fn_stdout = (
                f"/Users/qin/Desktop/_get_static_ip_stdout{uuid.uuid4()}.json"
            )
            self.__fn_tderr = (
                f"/Users/qin/Desktop/_get_static_ip_stderr{uuid.uuid4()}.json"
            )
        else:
            self.__file_path = "/root/logs.txt"
            self.__fn_stdout = f"/root/_get_static_ip_stdout{uuid.uuid4()}.json"
            self.__fn_tderr = f"/root/_get_static_ip_stderr{uuid.uuid4()}.json"

    def __log(self, result):
        with open(self.__file_path, "a+") as f:
            f.write(f"{str(result)}\n")
        if os.path.getsize(self.__file_path) > 1024 * 512:
            with open(self.__file_path, "r") as f:
                content = f.readlines()
                os.remove(self.__file_path)

    def __exec_aws_command(self, command):
        self.__get_static_ip_stdout = open(self.__fn_stdout, "w+")
        self.__get_static_ip_stderr = open(self.__fn_tderr, "w+")
        process = subprocess.Popen(
            command,
            stdout=self.__get_static_ip_stdout,
            stderr=self.__get_static_ip_stderr,
            universal_newlines=True,
            shell=True,
        )
        process.wait()
        # reuslt
        aws_result = ""
        filesize = os.path.getsize(self.__fn_tderr)
        if filesize == 0:
            with open(self.__fn_stdout) as json_file:
                result = json.load(json_file)
                aws_result = result
        else:
            with open(self.__fn_tderr) as json_file:
                aws_result = json_file.read()
        # clean cache files
        os.remove(self.__fn_stdout)
        os.remove(self.__fn_tderr)
        # print(aws_result)
        self.__log(aws_result)
        return aws_result

    def _get_static_ip(self):
        # execute aws command
        cli_command = f"aws lightsail get-static-ip --static-ip-name StaticIp-1 --region {self.__region} --no-cli-pager"
        result = self.__exec_aws_command(cli_command)

    def _release_static_ip(self, _ips):
        result = ""
        try:
            if _ips == -1:
                return -1
            for ip in _ips:
                cli_command = f"aws lightsail --no-paginate  release-static-ip --static-ip-name {ip} --region {self.__region} --no-cli-pager"
                result = self.__exec_aws_command(cli_command)
                # print("_release_static_ip released a ip")
        except Exception as e:
            self.__log(f"[_release_static_ip] error:" + str(e) + " result:" + result)
            return -1

    def _get_unattached_static_ips(self):
        try:
            cli_command = f"aws lightsail --no-paginate  get-static-ips --region {self.__region} --no-cli-pager"
            result = self.__exec_aws_command(cli_command)
            unattached_ips = []
            for ip in result["staticIps"]:
                if ip["isAttached"] == False:
                    unattached_ips.append(ip["name"])
            return unattached_ips
        except Exception as e:
            self.__log(
                f"[_get_unattached_static_ips] error:" + str(e) + " result:" + result
            )
            return -1

    def _attach_static_ip(self, ip_name, _instance_name):
        try:
            cli_command = f"aws lightsail --no-paginate  attach-static-ip --static-ip-name {ip_name} --instance-name {_instance_name} --region {self.__region} --no-cli-pager"
            result = self.__exec_aws_command(cli_command)
            # print(result)
            if result["operations"][0]["status"] == "Succeeded":
                self.__log("_attach_static_ip success")
            else:
                self.__log(
                    "[error][_attach_static_ip]", "_attach_static_ip" + str(result)
                )
        except Exception as e:
            pass
            self.__log("[error][_attach_static_ip]", "_attach_static_ip" + str(e))

    def _replace_fargate(self):
        arn = self._list_task()
        self._create_ssr_task()
        self._stop_task(arn)

    def _create_ssr_task(self):
        cli_command = f"aws ecs run-task\
                        --cluster arn:aws:ecs:us-west-2:825807444916:cluster/QinCluster\
                        --network-configuration awsvpcConfiguration=\{{subnets=[subnet-59acc072,subnet-3691656b,subnet-da313691,subnet-669e841f],securityGroups=[sg-01c1819cdc065a550],assignPublicIp=ENABLED\}}\
                        --task-definition SSRFargate"
        result = self.__exec_aws_command(cli_command)
        print("result:" + str(result))
        try:
            if len(result["failures"]) == 0:
                self.__log(f"[_create_ssr_task] create task success")
                return True
        except Exception as e:
            self.__log(f"[_create_ssr_task] create task failed:" + str(e))
            return False

    def _list_task(self):
        cli_command = f"aws ecs list-tasks\
                        --cluster arn:aws:ecs:us-west-2:825807444916:cluster/QinCluster"
        result = self.__exec_aws_command(cli_command)
        print("result:" + str(result))
        try:
            if result["taskArns"]!="":
                self.__log(f"[_list_task] list task success")
                return result["taskArns"][0]
        except Exception as e:
            self.__log(f"[_create_ssr_task] create task failed:" + str(e))
            return ""

    def _stop_task(self,arn):
        cli_command = f"aws ecs stop-task\
                        --cluster arn:aws:ecs:us-west-2:825807444916:cluster/QinCluster\
                        --task {arn}"
        result = self.__exec_aws_command(cli_command)
        print("result:" + str(result))
        try:
            if result["taskArns"]!="":
                self.__log(f"[_list_task] list task success")
                return result["taskArns"][0]
        except Exception as e:
            self.__log(f"[_create_ssr_task] create task failed:" + str(e))
            return ""
if __name__ == "__main__":
    em = ECSManager()
    print(em._create_ssr_task())
    print(em._list_task())
    print(em._stop_task("arn:aws:ecs:us-west-2:825807444916:task/QinCluster/7ef95139876a4c3c9a843518a4a118ef"))
