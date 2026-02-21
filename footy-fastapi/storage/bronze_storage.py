import json
from pathlib import Path
from datetime import datetime, timezone
from loguru import logger

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_BRONZE_DATA_PATH = BASE_DIR / "data" / "bronze"

class BronzeStorage:
    """stores raw api to disk as json files"""

    def __init__(self, base_path: str = DEFAULT_BRONZE_DATA_PATH):
        self.base_path = Path(base_path)

    def _folder(self, competition: str, data_type: str) -> Path:
        folder = self.base_path / competition / data_type
        folder.mkdir(parents = True, exist_ok = True)
        return folder
    
    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    def write(self, competition: str, data_type: str, data: dict):
        """Writes the given data to a JSON file in the timestamped folder."""
        folder = self. _folder(competition, data_type)
        filepath = folder / f"{self._timestamp()}.json"
        filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        logger.success(f"Data written to {filepath}")
        return filepath
    
    def read_newest(self, competition: str, data_type: str) -> dict | None:
        """ Read the newest JSON file for the given competition and data type, returned as a dict. Returns None if no files are found."""
        folder = self._folder(competition, data_type)
        files = sorted(folder.glob("*.json"), reverse = True)
        if not files:
            logger.warning(f"No files found in {folder}")
            return None
        newest_file = files[0]
        logger.info(f"Reading data from the newest file: {newest_file}`")
        return json.loads(newest_file.read_text())
    
    def list_all_files(self, competition: str, data_type: str) -> list[Path]:
        """List all the sorted JSON files for the given competition and data type, returned as a list of Path objects"""
        return sorted(self._folder(competition, data_type).glob("*.json"), reverse = True)