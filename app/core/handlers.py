from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError, NotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": {
                    "type": "not_found",
                    "message": exc.message,
                },
            },
        )

    @app.exception_handler(AppError)
    async def app_error_exception_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "type": "application_error",
                    "message": exc.message,
                },
            },
        )