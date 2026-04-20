from fastapi import FastAPI

from app.core.config import settings
from app.core.handlers import register_exception_handlers
from app.modules.tasks.presentation.routes import router as tasks_router

app = FastAPI(title=settings.app_name)

register_exception_handlers(app)


@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running"}


app.include_router(tasks_router)