from fastapi import FastAPI

from app.core.config import settings
from app.modules.tasks.presentation.routes import router as tasks_router

app = FastAPI(title=settings.app_name)


@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running"}


app.include_router(tasks_router)