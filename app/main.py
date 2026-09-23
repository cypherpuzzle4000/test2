from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import Base, engine, get_db
from app.models import Task
from app.schemas import TaskCreate, TaskRead


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)


@app.get("/health/live", tags=["health"])
def liveness() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
def readiness(database: Session = Depends(get_db)) -> dict[str, str]:
    try:
        database.execute(text("SELECT 1"))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database is not ready") from error
    return {"status": "ready"}


@app.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, database: Session = Depends(get_db)) -> Task:
    task = Task(title=payload.title)
    database.add(task)
    database.commit()
    database.refresh(task)
    return task


@app.get("/tasks", response_model=list[TaskRead])
def list_tasks(database: Session = Depends(get_db)) -> list[Task]:
    return list(database.scalars(select(Task).order_by(Task.id.desc())))


@app.patch("/tasks/{task_id}/complete", response_model=TaskRead)
def complete_task(task_id: int, database: Session = Depends(get_db)) -> Task:
    task = database.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")
    task.completed = True
    database.commit()
    database.refresh(task)
    return task