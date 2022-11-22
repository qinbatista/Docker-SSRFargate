from math import fabs
import os
import time
import requests
import base64
import threading
import uuid
import subprocess
from socket import *
from datetime import datetime
import json
from ping3 import ping
class TestSSR:
    def __init__(self):
        self.__target_server = "us.qinyupeng.com"
        # https://domains.google.com/checkip banned by Chinese GFW
        self._get_ip_website = "https://checkip.amazonaws.com"
        self._last_ip = ""

    def _declare_alive(self):
        thread_refresh = threading.Thread(
            target=self.__thread_declare_alive, name="t1", args=())
        thread_refresh.start()

    def __thread_declare_alive(self):
        udpClient = socket(AF_INET, SOCK_DGRAM)
        while True:
            try:
                if True:
                    udpClient.sendto((gethostbyname(self.__target_server)+","+str(0)).encode(encoding="utf-8"), (self.__target_server, 7171))
                time.sleep(1)
            except Exception as e:
                pass

    def _lambda_handler(self):
        result = ping('u11s.qinyupeng.com')
        if result:
            print("Success")
        else:
            print("Failed with {}".format(r.ret_code))

if __name__ == '__main__':
    ss = TestSSR()
    # ss._declare_alive()
    ss._lambda_handler()
