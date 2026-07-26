from fastapi import FastAPI, Request, Response
from httpx import URL, AsyncClient, HTTPError

from src.core import config_settings

# Перед вызовом client.reques


async def proxy_pass(request: Request) -> Response:
    client: AsyncClient = request.app.state.client
    headers = dict(request.headers)
    try:
        res = await client.request(
            method=request.method,
            url=str(request.url.replace(netloc=config_settings.address)),
            headers=headers,
            content=await request.body(),
            params=request.query_params,
        )
    except HTTPError as e:
        return Response(content=f"Gateway Timeout - {e}", status_code=500)
    return Response(
        content=res.content,
        status_code=res.status_code,
        headers=dict(res.headers),
    )


async def proxy_pass_dict(data: dict, app: FastAPI) -> dict:
    client: AsyncClient = app.state.client
    target_host, target_port = config_settings.address.split(":")
    try:
        response = await client.request(
            method=data["method"],
            url=str(
                URL(data["url"]).copy_with(host=target_host, port=int(target_port))
            ),
            headers=data["headers"],
            content=data["body"].encode("utf-8"),
        )
    except HTTPError as e:
        return {
            "content": f"Gateway Timeout - {e}",
            "status_code": 504,
        }
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
