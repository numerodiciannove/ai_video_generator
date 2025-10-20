import asyncio
from pathlib import Path
from typing import Dict, Any


from app.schemas.urls_validator import ConfigModel
from app.services.file_downloader import AsyncDownloaderService
from app.services.text_to_speach import TextToSpeechService
from core.configs import test_request


class MediaProcessingService:
    def __init__(self, config: Dict[str, Any]):
        # Валидируем и собираем ссылки
        self.config = ConfigModel.collect_links(config)
        self.task_name = self.config["task_name"]

        # Инициализация сервисов
        self.tts_service = TextToSpeechService(task_name=self.task_name)
        self.video_downloader = AsyncDownloaderService(task_name=self.task_name)
        self.audio_downloader = AsyncDownloaderService(task_name=self.task_name)

    async def download_videos(self) -> Dict[str, list[Path]]:
        videos = self.config.get("video_blocks", {})
        if not videos:
            print("⚠️ Нет видео для скачивания")
            return {}
        print(f"⬇️ Скачиваем {sum(len(v) for v in videos.values())} видео...")
        return await self.video_downloader.download_blocks(videos, files_type="video")

    async def download_audios(self) -> Dict[str, list[Path]]:
        audios = self.config.get("audio_blocks", {})
        if not audios:
            print("⚠️ Нет аудио для скачивания")
            return {}
        print(f"⬇️ Скачиваем {sum(len(a) for a in audios.values())} аудио...")
        return await self.audio_downloader.download_blocks(audios, files_type="audio")

    async def generate_voices(self) -> Dict[str, list[str]]:
        voices = self.config.get("voice_blocks", {})
        if not voices:
            print("⚠️ Нет голосов для генерации")
            return {}
        print(f"🎙 Генерируем голоса для {len(voices)} блоков...")
        return await self.tts_service.generate_blocks(voices)

    async def process_all(self) -> Dict[str, Any]:
        print("🚀 Запуск обработки всех медиа...")

        videos_task = asyncio.create_task(self.download_videos())
        audios_task = asyncio.create_task(self.download_audios())
        voices_task = asyncio.create_task(self.generate_voices())

        videos, audios, voices = await asyncio.gather(videos_task, audios_task, voices_task)
        print("✅ Все медиа обработаны успешно")

        return {"videos": videos, "audios": audios, "voices": voices}



if __name__ == "__main__":

    async def main():
        service = MediaProcessingService(config=test_request)
        results = await service.process_all()

        print("\n📦 Результаты обработки медиа:")
        for media_type, blocks in results.items():
            print(f"\n{media_type}:")
            for block, files in blocks.items():
                for f in files:
                    print(f"  {block}: {f}")

        # service.clear_temp()

    asyncio.run(main())
