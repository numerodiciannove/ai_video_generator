from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException
from app.schemas.urls_validator import ConfigModel
from app.celery_media_tasks.tasks import process_movie


app = FastAPI()


@app.get("/")
async def health_check():
    return {"message": "Hello World"}


@app.post("/process_media")
async def process_media(config: ConfigModel):
    try:
        payload = config.model_dump()
        print(f"payload: {payload}")

        task = process_movie.apply_async(kwargs={"data": payload})

        print(f"Task queued: {task.id}")
        return {"task_id": task.id, "status": "queued"}
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e) )


@app.get("/task_status/{task_id}")
async def task_status(task_id: str):
    task_result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
