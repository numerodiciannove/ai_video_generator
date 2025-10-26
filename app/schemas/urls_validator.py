from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any


class VoiceItem(BaseModel):
    text: str
    voice: str

class ConfigModel(BaseModel):
    task_name: str
    videos: List[str] = []
    audios: List[str] = []
    voices: List[VoiceItem] = []

    model_config = ConfigDict(extra="allow")

    @classmethod
    def collect_links(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        videos, audios, voices = [], [], []

        # Process video_blocks
        video_blocks = data.get("video_blocks", {})
        for block_videos in video_blocks.values():
            if isinstance(block_videos, list):
                videos.extend(block_videos)

        # Process audio_blocks
        audio_blocks = data.get("audio_blocks", {})
        for block_audios in audio_blocks.values():
            if isinstance(block_audios, list):
                audios.extend(block_audios)

        # Process voice_blocks
        voice_blocks = data.get("voice_blocks", {})
        for block_voices in voice_blocks.values():
            if isinstance(block_voices, list):
                for item in block_voices:
                    if isinstance(item, dict) and "text" in item and "voice" in item:
                        voices.append(item)

        data["videos"] = videos
        data["audios"] = audios
        data["voices"] = voices
        return data
