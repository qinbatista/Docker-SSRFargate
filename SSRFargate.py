# -*- coding: utf-8 -*-
from ast import While
import subprocess
import uuid
import os
import json
import requests
import time
import threading
from socket import *
from datetime import datetime
import pytz
import platform
from ECSManager import ECSManager


class SSRFargate:
    def __init__(self):
        # self.__region = _region
        # self.__server_name = _server_name
        self.__received_count = 0
        self.__CN_timezone = pytz.timezone("Asia/Shanghai")
        self.__current_ip_from_udp = ""
        # self.__close_port = False
        self.__udpServer = socket(AF_INET, SOCK_DGRAM)
        self.__current_ip = ""
        if platform.system() == "Darwin":
            self.__file_path = "/Users/qin/Desktop/logs.txt"
        else:
            self.__file_path = "/root/logs.txt"
        self.__is_connect = ""
        self.__the_ip = ""
        self.__inaccessible_count = 0
        self.__record_time = datetime.now(self.__CN_timezone)
        self.__ave_time = 0
        with open("/google_key.txt", "r") as f:
            self.__google_key = f.readline()
        with open("/google_secret.txt", "r") as f:
            self.__google_secret = f.readline()
        self.__google_key = self.__google_key.strip()
        self.__google_secret = self.__google_secret.strip()
    def __log(self, result):
        # if os.path.isfile(self.__file_path)==False:
        # with open(self.__file_path,"a+") as f:pass
        # print("key:key"+str(len(content)))
        with open(self.__file_path, "a+") as f:
            f.write(f"{str(result)}\n")
        if os.path.getsize(self.__file_path) > 1024 * 512:
            with open(self.__file_path, "r") as f:
                content = f.readlines()
                # print("content:"+str(len(content)))
                os.remove(self.__file_path)

    def __get_host_ip(self):
        try:
            text = requests.get("https://checkip.amazonaws.com").text.strip()
            # self.__log("_get_host_ip", text)
            return text
        except Exception as e:
            self.__log(
                f"[_get_host_ip]using ip {self.__current_ip_from_udp}, error:" + str(e)
            )
            return self.__current_ip_from_udp

    def _post_ip_to_google_DNS(self):
        try:
            self.__the_ip = self.__get_host_ip()
            if self.__the_ip == self.__current_ip:
                return
            else:
                result = requests.post(
                    f"https://0CZAMRlonw60PWyg:77JKaTvVEfjbqOjA@domains.google.com/nic/update?hostname=us.qinyupeng.com&myip={self.__the_ip}"
                )
                self.__current_ip = self.__the_ip
        except Exception as e:
            self.__log(
                f"_post_ip_address:{str(e)} self.__current_ip_from_udp={str(self.__current_ip_from_udp)}"
            )

    def _thread_IP_poster(self):
        thread_refresh = threading.Thread(target=self.__IP_poster, name="t1", args=())
        thread_refresh.start()

    def __IP_poster(self):
        while True:
            self._post_ip_to_google_DNS()
            time.sleep(10)

    def _thread_SSR(self):
        thread_refresh = threading.Thread(target=self.__SSR, name="t1", args=())
        thread_refresh.start()

    def __SSR(self):
        p = subprocess.Popen(
            "python /usr/local/ssr/shadowsocks/server.py -c /etc/ssr.json",
            universal_newlines=True,
            shell=True,
        )
        p.wait()

    def _thread_listening_CN(self):
        thread_refresh = threading.Thread(
            target=self.__listening_CN, name="t1", args=()
        )
        thread_refresh.start()

    def __listening_CN(self):
        try:
            self.__udpServer = socket(AF_INET, SOCK_DGRAM)
            self.__udpServer.bind(("", 7171))
            while True:
                data, addr = self.__udpServer.recvfrom(1024)
                ip, port = addr
                print(f"{data.decode(encoding='utf-8')} {ip} {port}")
                # self.__udpServer.sendto(f"{ip}".encode('utf-8'), addr)
                # if int(datetime.now(self.__CN_timezone).strftime('%H'))>1 and int(datetime.now(self.__CN_timezone).strftime('%H'))<14:
                self.__received_count = 0
                message = data.decode(encoding="utf-8").split(",")
                if len(message) == 2:
                    self.__current_ip_from_udp = message[0]
                    self.__is_connect = message[1]
                    if self.__is_connect == "1":
                        self.__inaccessible_count = 0
                    else:
                        self.__inaccessible_count += 1
                else:
                    self.__current_ip_from_udp = message
                self.__log(
                    f"{str(datetime.now(self.__CN_timezone))} self.__inaccessible_count:{self.__inaccessible_count} self.__is_connect={self.__is_connect} self.__current_ip_from_udp={self.__current_ip_from_udp} from:{ip}:{port} the_ip:{self.__the_ip} count:{self.__received_count}"
                )
        except Exception as e:
            self.__log(f"{str(e)}")

    def _thread_ip_holding(self):
        thread_refresh = threading.Thread(target=self.__ip_holding, name="t1", args=())
        thread_refresh.start()

    def __ip_holding(self):
        while True:
            try:
                self.__received_count = self.__received_count - 10
                # self.__log(f"self.__received_count={self.__received_count}")
                if self.__received_count <= -300 or self.__inaccessible_count >= 3:
                    first_time = datetime.now(self.__CN_timezone)
                    self.__replace_fargate_ip()
                    second_time = datetime.now(self.__CN_timezone)
                    difference = second_time - first_time
                    last_time = datetime.now(self.__CN_timezone) - self.__record_time
                    if self.__ave_time == 0:
                        self.__ave_time = last_time.seconds
                    else:
                        self.__ave_time = (self.__ave_time + last_time.seconds) / 2
                    self.__log(
                        f"| Used:{ difference.seconds:2.2f} seconds | Duration:{last_time.seconds/3600:2.2f} hours | Ave:{self.__ave_time/3600:2.2f} hours | Count:{self.__received_count}"
                    )
                    self.__log("")
                    self.__record_time = datetime.now(self.__CN_timezone)
                    self.__received_count = 0
                    self.__inaccessible_count = 0
                time.sleep(60)
            except Exception as e:
                # pass
                self.__log(f"{str(e)}")

    def _thread_display_log(self):
        thread_refresh = threading.Thread(target=self.__display_log, name="t1", args=())
        thread_refresh.start()

    def __display_log(self):
        p = subprocess.Popen(
            "python3 /HttpRequest.py",
            universal_newlines=True,
            shell=True,
        )
        p.wait()
    def _replace_fargate_ip(self):
        em = ECSManager()
        em._replace_fargate()

    def _running(self):
        while True:
            time.sleep(10)


if __name__ == "__main__":
    sf = SSRFargate()
    sf._thread_display_log()
    sf._thread_IP_poster()
    sf._thread_SSR()
    sf._thread_listening_CN()
    sf._thread_ip_holding()
    sf._running()
