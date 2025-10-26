import asyncio
import shutil
from pathlib import Path
from typing import Dict, Any, List

from loguru import logger

from app.schemas.urls_validator import ConfigModel
from .file_downloader import AsyncDownloaderService
from .audio_overlay import AudioOverlayService
from .google_driver_uploadaer import GoogleDriveService
from .text_to_speach import TextToSpeechService
from .video_combiner import VideoCombinerService


class MediaProcessingService:
    BASE_TEMP_DIR = Path(__file__).resolve().parent.parent / "temp_files"

    def __init__(self, config: Dict[str, Any]):
        self.config = ConfigModel.collect_links(config)
        self.task_name = self.config.get("task_name", "default_project")

        self.tts_service = TextToSpeechService(task_name=self.task_name)
        self.video_downloader = AsyncDownloaderService(task_name=self.task_name)
        self.audio_downloader = AsyncDownloaderService(task_name=self.task_name)
        self.gdrive_service = GoogleDriveService(project_name=self.task_name)

    async def _download_videos(self) -> Dict[str, List[Path]]:
        videos = self.config.get("video_blocks", {})
        if not videos:
            print("No videos to download.")
            return {}
        print(f"Downloading {sum(len(v) for v in videos.values())} video files...")
        return await self.video_downloader.download_blocks(videos, files_type="video")

    async def _download_audios(self) -> Dict[str, List[Path]]:
        audios = self.config.get("audio_blocks", {})
        if not audios:
            print("No audio files to download.")
            return {}
        logger.info(f"Downloading {sum(len(a) for a in audios.values())} audio files...")
        return await self.audio_downloader.download_blocks(audios, files_type="audio")

    async def _generate_voices(self) -> Dict[str, List[str]]:
        voices = self.config.get("voice_blocks", {})
        if not voices:
            print("No voice blocks to generate.")
            return {}
        logger.info(f"Generating voices for {len(voices)} blocks...")
        return await self.tts_service.generate_blocks(voices)

    def _combine_videos(self) -> List[Path]:
        logger.info("Combining videos...")

        try:
            combiner = VideoCombinerService(task_name=self.task_name)
            combined_videos = combiner.generate_combinations()
            return combined_videos
        except Exception as e:
            logger.error(f"Error combining videos: {e}")
            return []

    def _overlay_audio(self):
        logger.info("Applying audio overlay to combined videos...")

        audio_overlay_service = AudioOverlayService(task_name=self.task_name)
        audio_overlay_service.overlay_audio()

    def _upload_to_drive(self) -> List[str]:
        logger.info("Uploading combined videos to Google Drive...")

        uploaded_files = self.gdrive_service.upload_files()
        logger.info(f"Uploaded {len(uploaded_files)} files to Google Drive.")
        return uploaded_files

    def _cleanup_temp_files(self):
        temp_project_dir = self.BASE_TEMP_DIR / self.task_name
        if temp_project_dir.exists() and temp_project_dir.is_dir():
            shutil.rmtree(temp_project_dir)
            logger.warning(f"Temporary files for project '{self.task_name}' have been removed.")

    async def process_all(self) -> Dict[str, Any]:
        logger.info("Starting media processing...")

        try:
            videos_task = asyncio.create_task(self._download_videos())
            audios_task = asyncio.create_task(self._download_audios())
            voices_task = asyncio.create_task(self._generate_voices())

            videos, audios, voices = await asyncio.gather(videos_task, audios_task, voices_task)
            logger.success("All media downloaded/generated successfully.")

            combined_videos = self._combine_videos()

            uploaded_files = []
            if combined_videos:
                self._overlay_audio()
                uploaded_files = self._upload_to_drive()
            else:
                logger.warning("No combined videos available for audio overlay or upload.")

            return {
                "videos": videos,
                "audios": audios,
                "voices": voices,
                "combined_videos": combined_videos,
                "uploaded_files": uploaded_files
            }

        finally:
            self._cleanup_temp_files()
