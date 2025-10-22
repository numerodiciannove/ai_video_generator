import asyncio

from celery import shared_task

from app.schemas.urls_validator import ConfigModel
from app.services.media_processing import MediaProcessingService


@shared_task(name="process_movie")
def process_movie(data: dict) -> None:
    print("process_media_task started")

    processed_config = ConfigModel.collect_links(data)
    service = MediaProcessingService(config=processed_config)

    asyncio.run(service.process_all())
    print("process_media_task finished")
    # return
