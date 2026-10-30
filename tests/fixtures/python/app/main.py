from fastapi import FastAPI, HTTPException, status
from typing import List
from datetime import datetime
from app.schemas import Task, TaskCreate

app = FastAPI(title="Task Management API", version="0.1.0")

tasks_db: List[dict] = []


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return tasks_db


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate):
    new_id = len(tasks_db) + 1
    new_task = {
        "id": new_id,
        "title": task_in.title,
        "description": task_in.description,
        "completed": task_in.completed,
        "created_at": datetime.now(),
    }
    tasks_db.append(new_task)
    return new_task
