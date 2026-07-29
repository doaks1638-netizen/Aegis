from fastapi import Request
from fastapi.responses import JSONResponse

from src.exceptions import RMTypeErr, UnknownIPErr

from .router import app


@app.exception_handler(RMTypeErr)
def rm_type_handler(request: Request, exc: RMTypeErr):
    return JSONResponse(
        content={
            "error": "There was a temporary error setting up the service. We apologize."
        },
        status_code=500,
    )


@app.exception_handler(UnknownIPErr)
def unknown_ip_handler(request: Request, exc: UnknownIPErr):
    return JSONResponse(
        content={"error": "Your IP has not been identified."},
        status_code=502,
    )
