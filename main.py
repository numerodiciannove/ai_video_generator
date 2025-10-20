from typing import Dict, Any

from fastapi import FastAPI, HTTPException

from app.schemas.urls_validator import ConfigModel
from app.services.media_processing import MediaProcessingService

app = FastAPI()


@app.get("/")
async def health_check():
    return {"message": "Hello World"}

@app.post("/process_media")
async def process_media(config: ConfigModel):
    """
    Endpoint accepts JSON configuration:
    - task_name: name of the task
    - video_blocks: dictionary of video blocks
    - audio_blocks: dictionary of audio blocks
    - voice_blocks: dictionary for TTS generation
    """
    try:
        # Collect all links into standard lists
        processed_data = ConfigModel.collect_links(config.model_dump())

        # Initialize the media processing service
        service = MediaProcessingService(config=processed_data)

        # Asynchronously process videos, audios, and TTS
        result = await service.process_all()

        return {
            "status": "success",
            "videos": [str(p) for p in result["videos"]],
            "audios": [str(p) for p in result["audios"]],
            "voices": result["voices"]
        }

    except Exception as e:
        print(f"❌ Error during processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
