from itertools import product
from pathlib import Path
from typing import Any


class CombinationService:
    BASE_TEMP_DIR = Path(__file__).resolve().parent.parent / "temp_files"

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.output_dir = self.BASE_TEMP_DIR / task_name / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def generate_combinations(video_blocks: dict) -> list[tuple[Any, ...]]:
        """
        Generates all possible combinations of videos from blocks.
        """
        blocks = [v for k, v in sorted(video_blocks.items())]
        return list(product(*blocks))

    def get_output_path(self, idx: int) -> Path:
        """
        Path for saving final video
        """
        return self.output_dir / f"combo_{idx:03d}.mp4"
