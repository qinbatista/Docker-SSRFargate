# -*- coding: utf-8 -*-
import subprocess
import uuid
import os
import json
import platform
import getpass

class S3Manager:
    def __init__(self):
        if platform.system() == "Darwin":
            self.__file_path = f"/Users/{getpass.getuser()}/Desktop/logs.txt"
            self.__fn_stdout = (f"/Users/{getpass.getuser()}/Desktop/_get_static_ip_stdout{uuid.uuid4()}.json")
            self.__fn_tderr = (f"/Users/{getpass.getuser()}/Desktop/_get_static_ip_stderr{uuid.uuid4()}.json")
        else:
            self.__file_path = "/download/s3logs.txt"
            self.__fn_stdout = f"/download/_get_static_ip_stdout{uuid.uuid4()}.json"
            self.__fn_tderr = f"/download/_get_static_ip_stderr{uuid.uuid4()}.json"
        self.__s3_bucket = "s3://qinyupeng.com"

    def __log(self, result):
        if os.path.isfile(self.__file_path) == False:
            return
        with open(self.__file_path, "a+") as f:
            f.write(f"{str(result)}\n")
        if os.path.getsize(self.__file_path) > 1024 * 512:
            with open(self.__file_path, "r") as f:
                content = f.readlines()
                os.remove(self.__file_path)

    def __exec_aws_command(self, command)->list:
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

        aws_result = []
        filesize = os.path.getsize(self.__fn_tderr)
        if filesize == 0:
            with open(self.__fn_stdout) as json_file:
                aws_result = json_file.readlines()
        else:
            with open(self.__fn_tderr) as json_file:
                aws_result[0] = json_file.read()
        # clean cache files
        os.remove(self.__fn_stdout)
        os.remove(self.__fn_tderr)
        # print(aws_result)
        self.__log(aws_result)
        return aws_result

    def _list_folder(self, _folder_name)->list:
        cli_command = f'aws s3 ls {self.__s3_bucket}{_folder_name}'
        result = self.__exec_aws_command(cli_command)
        try:
            if len(result) > 0:
                self.__log(f"[_sync_folder] success")
                return result
            else:
                return []
        except Exception as e:
            self.__log(f"[_sync_folder] failed:" + str(e))
            return []

    def _sync_folder(self, source, _folder_name):
        cli_command = f'aws s3 cp {source} {self.__s3_bucket}{_folder_name} --recursive --storage-class DEEP_ARCHIVE --exclude "*" --include "*.mp4"'
        result = self.__exec_aws_command(cli_command)
        try:
            if "upload" in result[len(result) - 1]:  # type: ignore
                self.__log(f"[_sync_folder] success")
                return True
        except Exception as e:
            self.__log(f"[_sync_folder] failed:" + str(e))
            return False


if __name__ == "__main__":
    ss = S3Manager()
    # ss._sync_folder("/Users/batista/Desktop/文昭思绪飞扬", "/Videos/文昭思绪飞扬")
    ss._list_folder("/Videos/文昭思绪飞扬/")
