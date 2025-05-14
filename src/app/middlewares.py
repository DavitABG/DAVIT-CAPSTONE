"""
Here are stored custom middlewares
"""
import logging
import time

import fastapi
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       StreamingResponse,
                                       Request,
                                       RequestResponseEndpoint)
from starlette.responses import JSONResponse

from src.utils import generate_guid


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


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Basic logging middleware inherited from starlette.BaseHTTPMiddleware
    """

    def __init__(self, app: fastapi.FastAPI, logger: logging.Logger):
        """
        Init object with src and logger

        Parameters
        ----------
        app : fast.FastAPI
            actions object where middleware need to be added
        logger : logging.Logger
            already configured logger for logging requests
        """
        super().__init__(app)
        self.logger = logger

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        """
        Overriding BaseHTTPMiddleware.dispatch method to implement logging logic

        Parameters
        ----------
        request : starlette.middleware.base.Request
            current request
        call_next : starlette.middleware.base.RequestResponseEndpoint
            call function

        Returns
        -------

        streaming_response : starlette.middleware.base.StreamingResponse
            streaming response for the endpoint
        """
        guid = generate_guid()
        self.logger.info(f"rid={guid} start request path={request.url.path}")
        start_time = time.time()

        streaming_response = await call_next(request)
        status_code = streaming_response.status_code
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = '{0:.2f}'.format(process_time)
        # collect errors and log also error messages
        if not 200 <= status_code <= 299:
            logging_level = logging.ERROR if status_code >= 500 else (
                logging.WARNING)

            response_body = [
                section async for section in streaming_response.body_iterator
            ]
            streaming_response.body_iterator = iterate_in_threadpool(
                iter(response_body)
            )
            msg = ''
            if response_body:  # In case there's no body
                msg = response_body[0].decode()
            self.logger.log(
                msg=f"rid={guid} completed_in={formatted_process_time}ms"
                    f" status_code={status_code}"
                    f" message = {msg}",
                level=logging_level
            )

        else:
            self.logger.info(
                f"rid={guid} completed_in={formatted_process_time}ms "
                f"status_code={status_code}"
            )

        return streaming_response


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """A middleware to handle errors"""

    async def dispatch(self, request: Request, call_next):
        """Try to process the request. If failed, return details about the
        exception"""
        try:
            return await call_next(request)
        # Here goes the custom exception handling
        except Exception as e:
            info = self.extract_info(e)
            status_code = 500
        content = {"detail": [info]}
        return JSONResponse(status_code=status_code, content=content)

    @staticmethod
    def extract_info(error: Exception):
        """Extract the type and the message of an error and return as a dict"""
        return {"type": type(error).__name__,
                "msg": str(error)}


class TimingMiddleware(BaseHTTPMiddleware):
    """A middleware that adds processing time to response headers"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        """
        Add the full processing time of the request to the response headers

        Parameters
        ----------
        request : starlette.middleware.base.Request
            current request
        call_next : starlette.middleware.base.RequestResponseEndpoint
            call function

        Returns
        -------
        streaming_response : starlette.middleware.base.StreamingResponse
            streaming response for the endpoint
        """
        start_time = time.perf_counter()
        streaming_response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000  # seconds to milliseconds
        formatted_process_time = "{0:.2f}".format(process_time)
        streaming_response.headers["X-Full-Process-Time"] = f"{formatted_process_time} ms"
        return streaming_response
