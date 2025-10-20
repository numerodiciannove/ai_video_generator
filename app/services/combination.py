from itertools import product
from pathlib import Path
from typing import Any


class CombinationService:
    BASE_TEMP_DIR = Path(__file__).resolve().parent.parent / "temp_files"

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.output_dir = self.BASE_TEMP_DIR / task_name / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_combinations(self, video_blocks: dict) -> list[tuple[Any, ...]]:
        """
        Генерирует все возможные комбинации видео из блоков.
        """
        blocks = [v for k, v in sorted(video_blocks.items())]
        return list(product(*blocks))

    def get_output_path(self, idx: int) -> Path:
        """
        Путь для сохранения итогового видео
        """
        return self.output_dir / f"combo_{idx:03d}.mp4"
