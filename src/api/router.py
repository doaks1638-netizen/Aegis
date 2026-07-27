import json
from uuid import uuid4

import redis.exceptions as redis_exc
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from redis.asyncio import Redis

from src.core import config_settings
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
        # Decode bytes into a standard string (works for JSON and text)
        "body": (await request.body()).decode("utf-8"),
    }


@app.api_route("/{full_path:path}", methods=["GET", "PUT", "POST", "DELETE", "PATCH"])
async def handler_func(request: Request):
    logger.info(f"A request has arrived for - {request.url.path}")
    redis: Redis = request.app.state.redis
    status = await evaluate(request=request)
    if status == Action.BLOCK:
        logger.warning("Too many requests. Blocking")
        raise HTTPException(429, detail="Too Many Requests")
    if status == Action.PROXY:
        logger.info("Proxy the request")
        return await proxy_pass(request=request)
    else:
        _, general, queue_need, is_overloaded = status
    if is_overloaded:
        raise HTTPException(
            429, detail="The server is overloaded, please try your request later."
        )
    if queue_need:  # TODO: rename to wait_need
        lock_key = f"key:{uuid4()}"
        value = {"lock": lock_key, "request": await request_to_dict(request=request)}
        await put_task(
            request=request, path=request.url.path, general=general, value=value
        )
        logger.info("We are waiting for the lock to be removed.")
        try:
            result = await redis.blpop(lock_key, timeout=5)
        except redis_exc.TimeoutError:  # Called if the socket has gone down.
            logger.error("Failed to complete the task")
            raise HTTPException(504, detail="Failed to get response!")
        if result is None:
            logger.error("Failed to complete the task")
            raise HTTPException(504, detail="Failed to get response!")
        _, value = result
        return Response(**json.loads(value))

    else:
        value = {"lock": None, "request": await request_to_dict(request=request)}
        logger.info("We put it in the queue and return the code")
        await put_task(
            request=request, path=request.url.path, general=general, value=value
        )
        return JSONResponse(
            status_code=config_settings.response_code,
            content="Data successfully received. Processing will be finished soon!",
        )
