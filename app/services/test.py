import asyncio

from app.services.file_downloader import AsyncDownloaderService
from app.services.text_to_speach import TextToSpeechService
from core.configs import test_request

if __name__ == "__main__":
    async def process_task(request: dict):
        """Асинхронно выполняет все задачи — скачивание и TTS"""
        task_name = request["task_name"]
        downloader = AsyncDownloaderService(task_name)
        tts = TextToSpeechService(task_name)

        # Запускаем все задачи параллельно
        video_task = asyncio.create_task(downloader.download_blocks(request["video_blocks"], "video"))
        audio_task = asyncio.create_task(downloader.download_blocks(request["audio_blocks"], "audio"))
        tts_task = asyncio.create_task(tts.generate_blocks(request["voice_blocks"]))

        results = await asyncio.gather(video_task, audio_task, tts_task)

        return {
            "video_results": results[0],
            "audio_results": results[1],
            "voice_results": results[2],
        }


    asyncio.run(process_task(test_request))
