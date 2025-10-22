import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from urllib.parse import urlparse
import os

from loguru import logger


class AsyncDownloaderService:
    BASE_TEMP_DIR = Path(__file__).resolve().parent.parent.parent / "temp_files"
    MAX_CONCURRENT: int = 3

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)

    async def _download_one(self, session: aiohttp.ClientSession, url: str, save_dir: Path) -> Path | None:
        """Downloads one file"""
        async with self.semaphore:
            filename = os.path.basename(urlparse(url).path) or "file"
            file_path = save_dir / filename
            save_dir.mkdir(parents=True, exist_ok=True)

            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    async with aiofiles.open(file_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(1024 * 64):
                            await f.write(chunk)
                logger.info(f"✅ Downloaded: {file_path}")
                return file_path
            except Exception as e:
                logger.error(f"❌ Error downloading {url}: {e}")
                return None

    async def download_blocks(self, files_dict: dict, files_type: str) -> dict[str, list[Path]]:
        """
        Downloads all files from dictionary (block1, block2...) and saves to subfolders.
        """
        base_dir = self.BASE_TEMP_DIR / self.task_name / files_type
        base_dir.mkdir(parents=True, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            all_results = {}

            async def process_block(block_name, urls):
                block_dir = base_dir / block_name
                tasks = [self._download_one(session, url, block_dir) for url in urls]
                results = await asyncio.gather(*tasks)
                all_results[block_name] = [r for r in results if r]

            await asyncio.gather(*(process_block(b, u) for b, u in files_dict.items()))

        return all_results
