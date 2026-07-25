import json
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from redis import Redis

from src.core import config_settings, router_paths
from src.lifespan import lifespan
from src.queue import put_task
from src.rm import Action, evaluate

from .redirect import proxy_pass

app = FastAPI(lifespan=lifespan)


async def request_to_dict(request: Request) -> dict:
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        # Декодируем байты в обычную строку (работает для JSON и текста)
        "body": (await request.body()).decode("utf-8"),
    }


@app.api_route("/{full_path:path}", methods=["GET", "PUT", "POST", "DELETE", "PATCH"])
async def handler_func(request: Request):
    redis: Redis = request.app.state.redis
    status = await evaluate(request=request)
    if status == Action.BLOCK:
        raise HTTPException(429, detail="Too Many Requests")
    if status == Action.PROXY:
        return await proxy_pass(request=request)
    else:
        _, general = status
    if (not general and not config_settings.server_queue) or (
        general and not router_paths[request.url.path].queue
    ):
        lock_key = f"key:{uuid4()}"
        value = {"lock": lock_key, "request": await request_to_dict(request=request)}
        await put_task(
            request=request, path=request.url.path, general=general, value=value
        )
        result = await redis.blpop(lock_key, timeout=15)
        if result is None:
            raise HTTPException(504, detail="Не удалось получить ответ!")
        _, value = result
        return Response(**json.loads(value))

    else:
        value = {"lock": None, "request": await request_to_dict(request=request)}
        await put_task(
            request=request, path=request.url.path, general=general, value=value
        )
        return JSONResponse(
            status_code=config_settings.response_code,
            content="Данные успешно получены. Скоро все будет обработано!",
        )
