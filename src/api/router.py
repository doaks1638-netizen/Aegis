from fastapi import FastAPI, Request

app = FastAPI()


@app.api_route("/{full_path:path}", methods=["GET", "PUT", "POST", "DELETE", "PATCH"])
async def handler_func(requst: Request):
    pass
