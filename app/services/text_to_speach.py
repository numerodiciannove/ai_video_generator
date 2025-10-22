import os
from dotenv import load_dotenv

import asyncio
from pathlib import Path
import uuid
from datetime import datetime

from elevenlabs import ElevenLabs
from loguru import logger


load_dotenv()

ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")

class TextToSpeechService:
    BASE_TEMP_DIR = Path(__file__).resolve().parent.parent.parent / "temp_files"

    MAX_CONCURRENT = 3
    MODEL_ID = "eleven_multilingual_v2"
    AUDIO_FORMAT = "mp3_44100_128"

    def __init__(self, task_name: str, api_key: str = ELEVEN_LABS_API_KEY):
        self.task_name = task_name
        self.task_dir = self.BASE_TEMP_DIR / task_name / "voice"
        self.task_dir.mkdir(parents=True, exist_ok=True)

        self.client = ElevenLabs(api_key=api_key)
        self.semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)

    def get_all_voices(self) -> list[dict]:
        """Get all voices"""
        response = self.client.voices.get_all(show_legacy=True)
        voices = response.voices

        return [
            {"voice_id": v.voice_id, "name": v.name, "preview_url": getattr(v, "preview_url", None)}
            for v in voices
        ]

    def get_voice_id_by_name(self, name: str) -> str | None:
        for v in self.get_all_voices():
            if v["name"].lower() == name.lower():
                return v["voice_id"]
        return None

    def generate_and_save_voice_sync(self, text: str, voice_name: str, save_dir: Path) -> str:
        """Synchronous audio generation (without aiofiles)"""
        voice_id = self.get_voice_id_by_name(voice_name)
        if not voice_id:
            raise ValueError(f"Voice '{voice_name}' not found")

        save_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:4]
        filename = f"tts_{voice_name.lower()}_{timestamp}_{unique_id}.mp3"
        file_path = save_dir / filename

        audio_gen = self.client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=self.MODEL_ID,
            output_format=self.AUDIO_FORMAT,
        )

        with open(file_path, "wb") as f:
            for chunk in audio_gen:
                f.write(chunk)

        if file_path.stat().st_size == 0:
            raise RuntimeError(f"Audio not generated: {file_path}")

        logger.info(f"Voice saved: {file_path}")
        return str(file_path)

    async def generate_and_save_voice(self, text: str, voice_name: str, save_dir: Path) -> str:
        """Asynchronous wrapper over sync method"""
        async with self.semaphore:
            return await asyncio.to_thread(self.generate_and_save_voice_sync, text, voice_name, save_dir)

    async def generate_blocks(self, voice_blocks: dict) -> dict[str, list[str]]:
        """Asynchronous processing of multiple TTS blocks"""
        results = {}

        async def process_voice(block_name, item):
            try:
                save_dir = self.task_dir / block_name
                path = await self.generate_and_save_voice(item["text"], item["voice"], save_dir)
                results.setdefault(block_name, []).append(path)
            except Exception as e:
                logger.error(f"Error ({block_name}/{item['voice']}): {e}")

        tasks = [process_voice(block, item) for block, items in voice_blocks.items() for item in items]
        await asyncio.gather(*tasks)
        return results
