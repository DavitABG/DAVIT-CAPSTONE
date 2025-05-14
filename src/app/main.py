"""
---------------------------------------------
Main file for creating fastapi.FastAPI object
---------------------------------------------
"""

from fastapi import FastAPI

from src.app.middlewares import LoggingMiddleware, ExceptionHandlerMiddleware, TimingMiddleware
from src.app.routers import example_router, health
from src.config import APP_SETTINGS
from src.globals import logger

# Instantiate the actions with documentation settings
app = FastAPI(**APP_SETTINGS.model_dump(by_alias=True))

# add middlewares. ORDER IS IMPORTANT!!!
app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(LoggingMiddleware, logger=logger)
app.add_middleware(TimingMiddleware)

# add routers
app.include_router(example_router.router, prefix="")
app.include_router(health.router, prefix="")
