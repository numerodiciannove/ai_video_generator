import itertools
from pathlib import Path

from moviepy import VideoFileClip, concatenate_videoclips


class VideoCombinerService:
    BASE_TEMP_DIR = Path(__file__).resolve().parent.parent / "temp_files"

    DEFAULT_CODEC = "libx264"
    DEFAULT_AUDIO_CODEC = "aac"
    DEFAULT_FPS = 5

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.task_dir = self.BASE_TEMP_DIR / task_name / "video"
        if not self.task_dir.exists():
            raise FileNotFoundError(f"Папка с видео не найдена: {self.task_dir}")

        self.output_dir = self.BASE_TEMP_DIR / task_name / "combined_movies_raw"
        self.output_dir.mkdir(parents=True, exist_ok=True)

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
        """Создаёт все комбинации видео из блоков и сохраняет их"""
        blocks = self._get_video_blocks()
        block_names = list(blocks.keys())
        block_lists = [blocks[name] for name in block_names]

        all_combinations = list(itertools.product(*block_lists))
        print(f"🔗 Всего комбинаций: {len(all_combinations)}")

        output_paths = []

        for idx, combination in enumerate(all_combinations, start=1):
            clips = [VideoFileClip(str(v)) for v in combination]
            final_clip = concatenate_videoclips(clips, method="compose")

            combo_name = "_".join([v.stem for v in combination])
            out_path = self.output_dir / f"{combo_name}.mp4"
            final_clip.write_videofile(
                str(out_path),
                codec=self.DEFAULT_CODEC,
                audio_codec=self.DEFAULT_AUDIO_CODEC,
                fps=self.DEFAULT_FPS
            )

            final_clip.close()
            for c in clips:
                c.close()

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
