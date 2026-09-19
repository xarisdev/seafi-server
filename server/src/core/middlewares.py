import time
import logging

from uuid import uuid4

from fastapi import Request, Response

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("api_tracker")

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        request_id = str(uuid4())[:8]

        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)

        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8") if body_bytes else "None"

        async def receive():
            return {
                "type": "http.request",
                "body": body_bytes,
                "more_body": False
            }
        request._receive = receive

        logger.info(f"[{request_id}] Request | {method} {path} | Query: {query_params} | {body_str}")

        try:
            response = await call_next(request)
            duration = (time.perf_counter() - start_time) * 1000

            logger.info(f"[{request_id}] OUTBOUND | {method} {path} | Status: {response.status_code} | Took: {duration:.2f}ms",
            )

            response.headers["X-Request-Id"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.2f}ms"
            return response
        
        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"[{request_id}] Request failed | Took: {duration:.2f} | Error: {exc}", exc_info=True)
            raise