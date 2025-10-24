import os
import platform
import subprocess
import random
import re
from pathlib import Path

import urllib.request
import zipfile
import tarfile

from loguru import logger


class AudioOverlayService:
    BASE_TEMP_DIR = Path(__file__).resolve().parent.parent.parent / "temp_files"
    BIN_DIR = Path(__file__).resolve().parent.parent.parent / "bin" / "ffmpeg"

    FFMPEG_PATH = Path(__file__).resolve().parent.parent.parent / "bin" / "ffmpeg"
    BG_VOLUME = 0.2
    AUDIO_CODEC = "aac"
    AUDIO_SAMPLE_RATE = 44100
    AUDIO_CHANNELS = 2
    TEMP_AUDIO_DIR_NAME = "tmp_audio"

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.base_dir = self.BASE_TEMP_DIR / task_name

        self.input_videos_dir = self.base_dir / "combined_movies_raw"
        self.done_dir = self.base_dir / "done"
        self.done_dir.mkdir(exist_ok=True)

        self.bg_audio_dir = self.base_dir / "audio"
        self.voice_dir = self.base_dir / "voice"
        self.temp_audio_dir = self.base_dir / self.TEMP_AUDIO_DIR_NAME
        self.temp_audio_dir.mkdir(exist_ok=True)

        self.bg_audios = list(self.bg_audio_dir.glob("**/*.*"))
        self.voice_audios = list(self.voice_dir.glob("**/*.*"))
        self.videos = list(self.input_videos_dir.glob("*.mp4"))

        if not self.bg_audios:
            raise ValueError("No background audio")
        if not self.voice_audios:
            raise ValueError("No voice audio")
        if not self.videos:
            raise ValueError("No videos to process")

        self.FFMPEG_PATH = self._ensure_ffmpeg()

    def _ensure_ffmpeg(self) -> str:
        self.BIN_DIR.mkdir(parents=True, exist_ok=True)

        system = platform.system().lower()
        ffmpeg_exe = "ffmpeg.exe" if system == "windows" else "ffmpeg"
        ffmpeg_path = self.BIN_DIR / ffmpeg_exe

        if ffmpeg_path.exists():
            return str(ffmpeg_path)

        logger.info(f"Downloading ffmpeg for {system}...")

        if system == "windows":
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            zip_path = self.BIN_DIR / "ffmpeg.zip"
            urllib.request.urlretrieve(url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for f in zip_ref.namelist():
                    if f.endswith("bin/ffmpeg.exe"):
                        zip_ref.extract(f, self.BIN_DIR)
                        os.rename(self.BIN_DIR / f, ffmpeg_path)
            zip_path.unlink()
        elif system == "linux":
            url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
            tar_path = self.BIN_DIR / "ffmpeg.tar.xz"
            urllib.request.urlretrieve(url, tar_path)
            with tarfile.open(tar_path) as tar_ref:
                for f in tar_ref.getmembers():
                    if f.name.endswith("/ffmpeg"):
                        tar_ref.extract(f, self.BIN_DIR)
                        os.rename(self.BIN_DIR / f.name, ffmpeg_path)
                        os.chmod(ffmpeg_path, 0o755)
            tar_path.unlink()
        else:
            raise RuntimeError(f"Unsupported OS: {system}")

        logger.info(f"ffmpeg ready: {ffmpeg_path}")
        return str(ffmpeg_path)

    def _recode_audio(self, audio_path: Path) -> Path | None:
        output_path = self.temp_audio_dir / audio_path.name
        try:
            subprocess.run([
                str(self.FFMPEG_PATH),
                "-y",
                "-i", str(audio_path),
                "-ar", str(self.AUDIO_SAMPLE_RATE),
                "-ac", str(self.AUDIO_CHANNELS),
                "-c:a", "mp3",
                str(output_path)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output_path
        except subprocess.CalledProcessError:
            logger.warning(f"Skipping corrupted audio file: {audio_path.name}")
            return None

    def _get_duration(self, path: Path) -> float:
        process = subprocess.run([str(self.FFMPEG_PATH), "-i", str(path)],
                                 stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        match = re.search(r"Duration: (\d+):(\d+):(\d+).(\d+)", process.stderr)
        if not match:
            return 0
        h, m, s, ms = map(int, match.groups())
        return h * 3600 + m * 60 + s + ms / 100

    def overlay_audio(self):
        for video_path in self.videos:
            bg_audio = random.choice(self.bg_audios)
            voice_audio = random.choice(self.voice_audios)

            bg_audio_fixed = self._recode_audio(bg_audio)
            voice_audio_fixed = self._recode_audio(voice_audio)

            if not bg_audio_fixed or not voice_audio_fixed:
                logger.warning(f"⚠️ Skipping video {video_path.name} due to corrupted audio")
                continue

            video_duration = self._get_duration(video_path)
            bg_duration = self._get_duration(bg_audio_fixed)

            # How many times to repeat background to cover video
            loop_count = int(video_duration // bg_duration) + 1

            output_path = self.done_dir / video_path.name

            # Repeat background using -stream_loop
            cmd = [
                str(self.FFMPEG_PATH),
                "-y",
                "-i", str(video_path),
                "-stream_loop", str(loop_count),
                "-i", str(bg_audio_fixed),
                "-i", str(voice_audio_fixed),
                "-filter_complex", (
                    f"[1:a]volume={self.BG_VOLUME}[a1];"
                    f"[a1][2:a]amix=inputs=2:duration=first[aout]"
                ),
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-ar", str(self.AUDIO_SAMPLE_RATE),
                "-ac", str(self.AUDIO_CHANNELS),
                "-shortest",
                str(output_path)
            ]

            subprocess.run(cmd, check=True)
            logger.info(f"Video processed: {output_path.name}")
