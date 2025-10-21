import random
import subprocess
from pathlib import Path
import re

class AudioOverlayService:
    FFMPEG_PATH = Path(__file__).resolve().parent.parent / "bin" / "ffmpeg" / "ffmpeg.exe"
    BG_VOLUME = 0.2
    AUDIO_CODEC = "aac"
    AUDIO_SAMPLE_RATE = 44100
    AUDIO_CHANNELS = 2
    TEMP_AUDIO_DIR_NAME = "tmp_audio"

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.base_dir = Path(__file__).resolve().parent.parent / "temp_files" / task_name

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
            raise ValueError("Нет фоновых аудио")
        if not self.voice_audios:
            raise ValueError("Нет voice аудио")
        if not self.videos:
            raise ValueError("Нет видео для обработки")

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
            print(f"⚠️ Пропускаем битый аудиофайл: {audio_path.name}")
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
                print(f"⚠️ Пропускаем видео {video_path.name} из-за битого аудио")
                continue

            video_duration = self._get_duration(video_path)
            bg_duration = self._get_duration(bg_audio_fixed)

            # сколько раз повторить фон, чтобы он покрывал видео
            loop_count = int(video_duration // bg_duration) + 1

            output_path = self.done_dir / video_path.name

            # повторяем фон с помощью -stream_loop
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
                "-c:v", "copy",  # видео без перекодирования
                "-c:a", "aac",
                "-ar", str(self.AUDIO_SAMPLE_RATE),
                "-ac", str(self.AUDIO_CHANNELS),
                "-shortest",  # обрезаем аудио до длины видео
                str(output_path)
            ]

            subprocess.run(cmd, check=True)
            print(f"✅ Обработано видео: {output_path.name}")

if __name__ == "__main__":
    task_name = "test_task_3blocks_with_audio"
    service = AudioOverlayService(task_name)

    print("🎧 Запускаем наложение аудио на видео...")
    service.overlay_audio()
    print("✅ Все видео обработаны")
