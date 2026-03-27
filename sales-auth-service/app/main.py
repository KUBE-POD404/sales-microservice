from app.core.logging_config import setup_logging
import os
from fastapi import FastAPI
from app.routers.v1.auth import router as auth_router
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.exceptions.handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.exceptions.custom_exceptions import AppException

setup_logging()

if os.getenv("ENVIRONMENT") == "production":
    docs_url = None
    redoc_url = None
    openapi_url = None
else:
    docs_url = "/api/v1/auth/docs"
    redoc_url = "/api/v1/auth/redoc"
    openapi_url = "/api/v1/auth/openapi.json"

app = FastAPI(
    title="Authentication Service",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)


app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth_router)