from fastapi import FastAPI, HTTPException

from app.schemas.urls_validator import ConfigModel
from app.services.media_processing import MediaProcessingService

app = FastAPI()


@app.get("/")
async def health_check():
    return {"message": "Hello World"}

@app.post("/process_media")
async def process_media(config: ConfigModel):
    try:
        processed_config = ConfigModel.collect_links(config.model_dump())
        service = MediaProcessingService(config=processed_config)
        results = await service.process_all()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
