import json
from aiohttp import web
import platform
import os

class HttpRequestManager:
    def __init__(self, worlds=[]):
        if platform.system() == "Darwin":
            self.__log_file_location = "/Users/qin/Desktop/logs.txt"
        else:
            self.__log_file_location = "/root/logs.txt"

    async def _get_log(self):
        if os.path.isfile(self.__log_file_location)==False: return "no file"
        content = ""
        with open(self.__log_file_location, "r") as f:
            content = f.readlines()
        return content


ROUTES = web.RouteTableDef()


def _json_response(body: dict = "", **kwargs) -> web.Response:
    kwargs["body"] = json.dumps(body or kwargs["kwargs"]).encode("utf-8")
    kwargs["content_type"] = "text/json"
    return web.Response(**kwargs)


@ROUTES.get("/")
async def get_log(request: web.Request) -> web.Response:
    result = await (request.app["MANAGER"])._get_log()
    return _json_response({"status": 200, "message": "health", "data": result})


def run():
    print("version:1.0")
    app = web.Application()
    app.add_routes(ROUTES)
    app["MANAGER"] = HttpRequestManager()
    web.run_app(app, port="7031")

if __name__ == "__main__":
    run()
