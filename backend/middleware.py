from __future__ import annotations

import logging
import time
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.exceptions import SmartBankError

logger = logging.getLogger("smartbank.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable],
    ) -> Response:  # noqa: F821
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        logger.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            elapsed_ms=round(elapsed * 1000, 2),
            ip=request.client.host if request.client else None,
        )
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable],
    ) -> Response:  # noqa: F821
        try:
            return await call_next(request)
        except SmartBankError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": {"code": exc.code, "detail": exc.detail}},
            )
        except Exception:
            logger.exception("Unhandled exception")
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "detail": "An unexpected error occurred",
                    }
                },
            )


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
