import json
from aiohttp import web
import platform
import os
import socket
import re
import requests
import subprocess


class HttpRequestManager:
    def __init__(self, worlds=[]):
        self.__file_path = "/http_request_logs.txt"

    def _get_files(self, path):
        files_dict = {}
        # Walk through all the files and subdirectories in the directory
        for root, dirs, files in os.walk(path):
            # For each file, add its name and path to the dictionary
            for file in files:
                file_path = os.path.join(root, file)
                files_dict[file] = file_path
        return files_dict

    # async def _check_query(self, path):
    #     if os.path.isfile(path):
    #         return self._get_files()
    #     else:
    #         return {"message": "no such folder"}

    async def _check_file_content(self, path):
        if os.path.isfile(path):
            with open(path, 'r') as f:
                file_contents = f.read()
            return {path: file_contents}
        elif os.path.isdir(path):
            return self._get_files(path)
        else:
            return {"message": "no such file or folder"}

    def check_ip_or_domain(self, string):
        ip_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        if re.match(ip_pattern, string):
            return "ip"
        else:
            return "domain"

    def _get_ip_from_domain(self, domain_name):
        try:
            return socket.gethostbyname(domain_name)
        except:
            return "Error: Unable to get IP for domain name"

    def get_ip_info(self, ip):
        try:
            output = subprocess.check_output(["whois", ip])
            output_str = output.decode("utf-8")
            response = requests.get(
                f"http://api.ipapi.com/api/{ip}?access_key=762f03e6b5ba38cff2fb5d876eb7860f&hostname=1", timeout=5).json()
            self.__log(f"response:{response}")
            del response["location"]
            response["whois"] = output_str
            if response.status_code == 200:
                return response
            else:
                return response
        except:
            self.__log(f"error response:{response}")
            return response

    def __log(self, result):
        with open(self.__file_path, "a+") as f:
            f.write(result+"\n")
        if os.path.getsize(self.__file_path) > 1024*128:
            with open(self.__file_path, "r") as f:
                content = f.readlines()
                os.remove(self.__file_path)

    async def _IP_function(self, value, remote_ip):
        if value == "myself":
            return self.get_ip_info(remote_ip)
        if self.check_ip_or_domain(value) == "ip":
            return self.get_ip_info(value)
        else:
            ip = self._get_ip_from_domain(value)
            return self.get_ip_info(ip)


ROUTES = web.RouteTableDef()


def _json_response(body: dict = "", **kwargs) -> web.Response:
    kwargs["body"] = json.dumps(body or kwargs["kwargs"]).encode("utf-8")
    kwargs["content_type"] = "text/json"
    return web.Response(**kwargs)

@ROUTES.get("/lookup")
async def query_message(request: web.Request) -> web.Response:
    result = await (request.app["MANAGER"])._check_file_content(request.query["path"])
    return _json_response(result)

@ROUTES.get("/ip/{value}")
async def get_log(request: web.Request) -> web.Response:
    result = await (request.app["MANAGER"])._IP_function(request.rel_url.name, request.remote)
    return _json_response(result)


# @ROUTES.get("/{value}")
# async def query_message(request: web.Request) -> web.Response:
#     result = await (request.app["MANAGER"])._check_query(request.rel_url.name)
#     return _json_response(result)

def run():
    print("HttpRequest:1.1")
    app = web.Application()
    app.add_routes(ROUTES)
    app["MANAGER"] = HttpRequestManager()
    web.run_app(app, port=7031)


if __name__ == "__main__":
    run()
