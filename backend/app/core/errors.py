"""Application-wide exception handling.

FastAPI already turns ``HTTPException`` and request-validation errors into
clean JSON responses. The gap is *uncaught* exceptions, which otherwise bubble
up as a bare 500 and can leak a traceback to the client. This registers a
catch-all handler that logs the full error server-side and returns a generic
JSON body instead.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("app")


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled exception during %s %s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the global exception handlers to ``app``."""
    app.add_exception_handler(Exception, unhandled_exception_handler)
