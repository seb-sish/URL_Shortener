from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

def register_exception_handlers(app: FastAPI):
    """
    Register custom exception handlers for the FastAPI application.
    """
    app.add_exception_handler(RequestValidationError, req_validation_exception_handler)
    app.add_exception_handler(ResponseValidationError, resp_validation_exception_handler)

async def req_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

async def resp_validation_exception_handler(response: Response, exc: ResponseValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )