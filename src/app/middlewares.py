import logging

from fastapi import HTTPException
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       StreamingResponse,
                                       Request)
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


async def resolve_response(
        streaming_response: StreamingResponse
) -> StreamingResponse:
    """
    Resole response

    Parameters
    ----------
    streaming_response : StreamingResponse
        response

    Returns
    -------
    streaming_response : StreamingResponse
        response
    """
    response_body = [section async for section in
                     streaming_response.body_iterator]
    streaming_response.body_iterator = iterate_in_threadpool(
        iter(response_body))
    return streaming_response


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as http_exception:
            return JSONResponse(
                status_code=http_exception.status_code,
                content={"error": "Client Error", "message": str(http_exception.detail)},
            )
        except Exception as e:
            logger.exception(msg=e.__class__.__name__, args=e.args)
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error", "message": "An unexpected error occurred."},
            )
