from fastapi import FastAPI, Request

from src.core import config_settings, router_paths

from .redicret import proxy_pass

app = FastAPI()


@app.api_route("/{full_path:path}", methods=["GET", "PUT", "POST", "DELETE", "PATCH"])
async def handler_func(requst: Request):
    if not config_settings.all_path:
        path = requst.url.path
        while path != "":
            if path in router_paths:
                break
            path = (path.rsplit("/", maxsplit=1)[0] or "/") if path != "/" else ""
        else:
            return await proxy_pass(requst)
