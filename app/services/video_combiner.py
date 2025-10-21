import os
import platform
import itertools
from pathlib import Path
import subprocess
import urllib.request
import zipfile
import tarfile

class VideoCombinerService:
    BASE_TEMP_DIR = Path(__file__).resolve().parent.parent / "temp_files"
    BIN_DIR = Path(__file__).resolve().parent.parent / "bin" / "ffmpeg"

    # === Общие настройки видео ===
    DEFAULT_CODEC = "libx264"
    DEFAULT_FPS = 10          # FPS для всех видео
    DEFAULT_WIDTH = 270       # ширина после ресайза
    DEFAULT_HEIGHT = 480     # высота после ресайза
    DEFAULT_SAR = 1           # pixel aspect ratio
    DEFAULT_OVERWRITE = True  # автоматически перезаписывать существующие файлы

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.task_dir = self.BASE_TEMP_DIR / task_name / "video"
        if not self.task_dir.exists():
            raise FileNotFoundError(f"Папка с видео не найдена: {self.task_dir}")

        self.output_dir = self.BASE_TEMP_DIR / task_name / "combined_movies_raw"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.codec = self.DEFAULT_CODEC
        self.fps = self.DEFAULT_FPS
        self.width = self.DEFAULT_WIDTH
        self.height = self.DEFAULT_HEIGHT
        self.sar = self.DEFAULT_SAR
        self.overwrite = self.DEFAULT_OVERWRITE

        # Проверяем и скачиваем ffmpeg локально
        self.ffmpeg_path = self._ensure_ffmpeg()

    def _ensure_ffmpeg(self) -> str:
        self.BIN_DIR.mkdir(parents=True, exist_ok=True)
        system = platform.system().lower()
        ffmpeg_exe = "ffmpeg.exe" if system == "windows" else "ffmpeg"
        ffmpeg_path = self.BIN_DIR / ffmpeg_exe

        if ffmpeg_path.exists():
            return str(ffmpeg_path)

        print(f"⬇️ Скачиваем ffmpeg для {system}...")

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

        print(f"✅ ffmpeg готов: {ffmpeg_path}")
        return str(ffmpeg_path)

    def _get_video_blocks(self) -> dict[str, list[Path]]:
        """Возвращает словарь блоков с путями к видеофайлам"""
        blocks = {}
        for block_path in sorted(self.task_dir.iterdir()):
            if block_path.is_dir():
                videos = sorted(block_path.glob("*.*"))
                if videos:
                    blocks[block_path.name] = videos
        if not blocks:
            raise ValueError(f"Нет видео в папках блоков: {self.task_dir}")
        return blocks

    def generate_combinations(self) -> list[Path]:
        blocks = self._get_video_blocks()
        block_names = list(blocks.keys())
        block_lists = [blocks[name] for name in block_names]

        all_combinations = list(itertools.product(*block_lists))
        print(f"🔗 Всего комбинаций: {len(all_combinations)}")

        output_paths = []

        for idx, combination in enumerate(all_combinations, start=1):
            combo_name = "_".join([v.stem for v in combination])
            out_path = self.output_dir / f"{combo_name}.mp4"

            input_args = []
            filter_parts = []

            for i, video in enumerate(combination):
                input_args.extend(["-i", str(video)])
                filter_parts.append(
                    f"[{i}:v]scale={self.width}:{self.height},fps={self.fps},setsar={self.sar}[v{i}];"
                )

            filter_complex = "".join(filter_parts) + "".join(
                f"[v{i}]" for i in range(len(combination))
            ) + f"concat=n={len(combination)}:v=1:a=0[outv]"

            cmd = [self.ffmpeg_path, *input_args,
                   "-filter_complex", filter_complex,
                   "-map", "[outv]",
                   "-c:v", self.codec]

            if self.overwrite:
                cmd.append("-y")

            cmd.append(str(out_path))

            subprocess.run(cmd, check=True)
            output_paths.append(out_path)
            print(f"✅ Сохранили комбинацию {idx}/{len(all_combinations)} -> {out_path.name}")

        return output_paths


if __name__ == "__main__":
    import time

    task_name = "test_task_3blocks_with_audio"

    try:
        combiner = VideoCombinerService(task_name=task_name)
    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}")
        exit(1)

    start_time = time.time()
    try:
        output_videos = combiner.generate_combinations()
    except ValueError as e:
        print(f"❌ Ошибка при генерации комбинаций: {e}")
        exit(1)
    end_time = time.time()

    print(f"\n🎬 Всего сгенерировано комбинаций: {len(output_videos)}")
    print(f"⏱ Время выполнения: {end_time - start_time:.2f} секунд")

    print("\nСгенерированные файлы:")
    for video_path in output_videos:
        print(f" - {video_path}")
