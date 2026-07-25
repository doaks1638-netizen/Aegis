from fastapi import FastAPI, Request, Response
from httpx import AsyncClient


async def proxy_pass(request: Request) -> Response:
    client: AsyncClient = request.app.state.client
    headers = dict(request.headers)
    res = await client.request(
        method=request.method,
        url=request.url,
        headers=headers,
        content=await request.body(),
        params=request.query_params,
    )
    return Response(
        content=res.content,
        status_code=res.status_code,
        headers=dict(res.headers),
    )


async def proxy_pass_dict(data: dict, app: FastAPI) -> dict:
    client: AsyncClient = app.state.client

    response = await client.request(
        method=data["method"],
        url=data["url"],
        headers=data["headers"],
        content=data["body"].encode("utf-8"),
    )

    headers = dict(response.headers)

    # remove headers that could break the response (since response.text is already decoded)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)

    return {
        "status_code": response.status_code,
        "content": response.text,
        "headers": headers,
        "media_type": response.headers.get("content-type"),
    }
