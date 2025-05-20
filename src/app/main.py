from fastapi import FastAPI

from src.app.middlewares import ExceptionHandlerMiddleware
from src.app.routers import pareto, health, customers, products, sales, preview
from src.config import APP_SETTINGS

# Instantiate the actions with documentation settings
app = FastAPI(**APP_SETTINGS.model_dump(by_alias=True))

# add middlewares. ORDER IS IMPORTANT!!!
app.add_middleware(ExceptionHandlerMiddleware)

# add routers
app.include_router(pareto.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(health.router)
app.include_router(preview.router)
