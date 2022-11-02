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

    def _replace_fargate(self):
        self.__log("_list_task")
        arn = self._list_task()
        self.__log("_create_ssr_task")
        self._create_ssr_task()
        self.__log("_stop_task")
        self._stop_task(arn)

    def _create_ssr_task(self):
        cli_command = f"aws ecs run-task\
                        --cluster arn:aws:ecs:us-west-2:825807444916:cluster/QinCluster\
                        --network-configuration awsvpcConfiguration=\{{subnets=[subnet-59acc072,subnet-3691656b,subnet-da313691,subnet-669e841f],securityGroups=[sg-01c1819cdc065a550],assignPublicIp=ENABLED\}}\
                        --task-definition SSRFargate"
        result = self.__exec_aws_command(cli_command)
        try:
            if len(result["failures"]) == 0:
                self.__log(f"[_create_ssr_task] create task success")
                return True
        except Exception as e:
            self.__log(f"[_create_ssr_task] failed:" + str(e))
            return False

    def _list_task(self):
        cli_command = f"aws ecs list-tasks\
                        --cluster arn:aws:ecs:us-west-2:825807444916:cluster/QinCluster"
        result = self.__exec_aws_command(cli_command)
        try:
            if result["taskArns"][0] != "":
                self.__log(f"[_list_task] list task success")
                return result["taskArns"][0]
        except Exception as e:
            self.__log(f"[_list_task] failed:" + str(e))
            return ""

    def _stop_task(self, arn):
        if arn=="": return
        cli_command = f"aws ecs stop-task\
                        --cluster arn:aws:ecs:us-west-2:825807444916:cluster/QinCluster\
                        --task {arn}"
        result = self.__exec_aws_command(cli_command)
        try:
            if result["taskArns"] != "":
                self.__log(f"[_stop_task] list task success")
                return result["taskArns"][0]
        except Exception as e:
            self.__log(f"[_stop_task] failed:" + str(e))
if __name__ == "__main__":
    ss = ECSManager()
    ss._replace_fargate()