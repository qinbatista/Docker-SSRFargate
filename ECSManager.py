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
            self.__file_path = "~/Desktop/logs.txt"
        else:
            self.__file_path = "/root/logs.txt"

    def __log(self, result):
        with open(self.__file_path, "a+") as f:
            f.write(f"{str(result)}\n")
        if os.path.getsize(self.__file_path) > 1024 * 512:
            with open(self.__file_path, "r") as f:
                content = f.readlines()
                os.remove(self.__file_path)

    def __exec_aws_command(self, command):
        _fn_stdout = f"/root/_get_static_ip_stdout{uuid.uuid4()}.json"
        _fn_tderr = f"/root/_get_static_ip_stderr{uuid.uuid4()}.json"
        _get_static_ip_stdout = open(_fn_stdout, "w+")
        _get_static_ip_stderr = open(_fn_tderr, "w+")
        process = subprocess.Popen(
            command,
            stdout=_get_static_ip_stdout,
            stderr=_get_static_ip_stderr,
            universal_newlines=True,
            shell=True,
        )
        process.wait()
        # reuslt
        aws_result = ""
        filesize = os.path.getsize(_fn_tderr)
        if filesize == 0:
            with open(_fn_stdout) as json_file:
                result = json.load(json_file)
                aws_result = result
        else:
            with open(_fn_tderr) as json_file:
                aws_result = json_file.read()
        # clean cache files
        os.remove(_fn_stdout)
        os.remove(_fn_tderr)
        # print(aws_result)
        self.__log(aws_result)
        return aws_result

    def _allocateIP(self):
        cli_command = f"aws lightsail --no-paginate allocate-static-ip --static-ip-name {uuid.uuid4()} --region {self.__region} --no-cli-pager"
        result = self.__exec_aws_command(cli_command)
        try:
            if result["operations"][0]["status"] == "Succeeded":
                # print("_allocateIP a ip")
                return result["operations"][0]["resourceName"]
        except Exception as e:
            self.__log(f"[_allocateIP] error:" + str(e))
            return -1

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
        pass
        # create a new fargate
        # close this fargate


if __name__ == "__main__":
    em = ECSManager()
    em._replace_fargate()
