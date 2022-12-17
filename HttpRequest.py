import json
from aiohttp import web
import platform
import os
import socket
import re
import requests


class HttpRequestManager:
    def __init__(self, worlds=[]):
        if platform.system() == "Darwin":
            self.__log_file_location = "/Users/qin/Desktop/logs.txt"
            self.__download = "/Users/qin/Downloads"
        else:
            self.__log_file_location = "/root/logs.txt"
            self.__download = "/download"

    async def _get_log(self):
        if os.path.isfile(self.__log_file_location) == False:
            return "no file"
        content = ""
        with open(self.__log_file_location, "r") as f:
            content = f.readlines()
        return content

    def _get_files(self):
        files_dict = {}
        # Walk through all the files and subdirectories in the directory
        for root, dirs, files in os.walk(self.__download):
            # For each file, add its name and path to the dictionary
            for file in files:
                file_path = os.path.join(root, file)
                files_dict[file] = file_path
        return files_dict

    async def _check_query(self, id):
        if id == "download":
            return self._get_files()
        else:
            return {"message": "no such id"}

    async def _check_file_content(self, path):
        if os.path.isfile(path) == False:
            return {path: "no such file"}
        with open(path, 'r') as f:
            file_contents = f.read()
        return {path: file_contents}

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
            response = requests.get(f"http://api.ipapi.com/api/{ip}?access_key=762f03e6b5ba38cff2fb5d876eb7860f")
            if response.status_code == 200:
                return response.json()
            else:
                return response.json()
        except:
            return response.json()

    async def _IP_function(self, value,remote_ip):
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


@ROUTES.get("/log")
async def get_log(request: web.Request) -> web.Response:
    result = await (request.app["MANAGER"])._get_log()
    return _json_response({"status": 200, "message": "health", "data": result})


@ROUTES.get("/ip/{value}")
async def get_log(request: web.Request) -> web.Response:
    result = await (request.app["MANAGER"])._IP_function(request.rel_url.name,request.remote)
    str_result = ""
    for key, value in result.items():
        str_result = str_result + "|"+str(key) + ":" + str(value)+"| "
    return _json_response(str_result)


@ROUTES.get("/{value}")
async def query_message(request: web.Request) -> web.Response:
    result = await (request.app["MANAGER"])._check_query(request.rel_url.name)
    return _json_response(result)


def run():
    print("version:1.0")
    app = web.Application()
    app.add_routes(ROUTES)
    app["MANAGER"] = HttpRequestManager()
    web.run_app(app, port="7031")


if __name__ == "__main__":
    run()
