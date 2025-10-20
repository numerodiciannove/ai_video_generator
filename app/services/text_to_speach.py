import asyncio
import aiofiles
from pathlib import Path
import uuid
from datetime import datetime
from elevenlabs import ElevenLabs

from core.configs import ELEVEN_LABS_API_KEY, test_request


class TextToSpeechService:
    BASE_TEMP_DIR = Path(__file__).resolve().parent.parent / "temp_files"

    def __init__(self,
                 task_name: str,
                 api_key: str = ELEVEN_LABS_API_KEY,
                 max_concurrent: int = 3
    ):
        self.task_name = task_name
        self.task_dir = self.BASE_TEMP_DIR / task_name / "voice"
        self.task_dir.mkdir(parents=True, exist_ok=True)
        self.max_concurrent = max_concurrent
        self.api_key = api_key
        self.client = ElevenLabs(api_key=self.api_key)

    def get_all_voices(self) -> list[dict]:
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

    async def generate_and_save_voice(self, text: str, voice_name: str, save_dir: Path) -> str:
        """Создаёт и сохраняет голос"""
        voice_id = self.get_voice_id_by_name(voice_name)
        if not voice_id:
            raise ValueError(f"Голос '{voice_name}' не найден")

        save_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:4]
        filename = f"tts_{voice_name.lower()}_{timestamp}_{unique_id}.mp3"
        file_path = save_dir / filename

        audio_gen = self.client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        async with aiofiles.open(file_path, "wb") as f:
            for chunk in audio_gen:
                await f.write(chunk)

        print(f"🎤 Сохранён голос: {file_path}")
        return str(file_path)

    async def generate_blocks(self, voice_blocks: dict) -> dict[str, list[str]]:
        """Асинхронно обрабатывает несколько блоков TTS"""
        results = {}
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def process_voice(block_name, item):
            async with semaphore:
                try:
                    save_dir = self.task_dir / block_name
                    path = await self.generate_and_save_voice(item["text"], item["voice"], save_dir)
                    results.setdefault(block_name, []).append(path)
                except Exception as e:
                    print(f"❌ Ошибка ({block_name}/{item['voice']}): {e}")

        tasks = [process_voice(block, item) for block, items in voice_blocks.items() for item in items]
        await asyncio.gather(*tasks)
        return results
