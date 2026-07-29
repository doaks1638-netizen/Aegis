import json
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from src.core import ags_logger as logger
from src.core import config_settings
from src.enums import Action
from src.lifespan import lifespan
from src.models import ActionGO, WaitStrategy
from src.queue import put_task
from src.rm import evaluate

from .redirect import proxy_pass

app = FastAPI(lifespan=lifespan)


async def request_to_dict(request: Request) -> dict:
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        # Decode bytes into a standard string (works for JSON and text)
        "body": (await request.body()).decode("utf-8"),  # pyright: ignore[reportAttributeAccessIssue]
    }


@app.api_route("/{full_path:path}", methods=["GET", "PUT", "POST", "DELETE", "PATCH"])
async def handler_func(request: Request):
    start = time.perf_counter()
    logger.info(
        f"REQUEST - {request.url=} - {request.headers.get('x-real-ip', 'NO IP')} - {request.method}"
    )
    redis: Redis = request.app.state.redis
    status: Action | ActionGO = await evaluate(request=request)
    if status == Action.BLOCK:
        logger.warning("Too many requests. Blocking")
        raise HTTPException(429, detail="Too Many Requests")
    if status == Action.PROXY:
        logger.info("Proxy the request")
        return await proxy_pass(request=request)
    if status == Action.ERROR:
        logger.error("The number of errors has exceeded the limit! Sending code 503.")
        raise HTTPException(503, detail="Server error. Please try again later.")
    if status == Action.OVERLOADED:
        raise HTTPException(
            429, detail="The server is overloaded, please try your request later."
        )
    if status.wait == WaitStrategy.SLOW:
        lock_key = f"key:{uuid4()}"
        value = {"lock": lock_key, "request": await request_to_dict(request=request)}
        await put_task(
            request=request,
            path=request.url.path,
            general=status.general,
            value=value,  # pyright: ignore[reportArgumentType]
        )
        logger.info("We are waiting for the lock to be removed.")
        async with redis.client() as redis_client:
            logger.info("Waiting for a response from Redis")
            result = await redis_client.blpop(lock_key)
        _, value = result  # pyright: ignore[reportGeneralTypeIssues]
        logger.info(
            f"We send a request to the client. The response time was - {time.perf_counter() - start} sec."
        )
        return Response(**json.loads(value))

    else:
        value = {"lock": None, "request": await request_to_dict(request=request)}
        logger.info("We put it in the queue and return the code")
        await put_task(
            request=request,
            path=request.url.path,
            general=status.general,
            value=value,  # pyright: ignore[reportArgumentType]
        )
        logger.info("We send a request to the client")
        return JSONResponse(
            status_code=config_settings.response_code,
            content="Data successfully received. Processing will be finished soon!",
        )
