from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CONFIG = BASE_DIR / "core" / "config.json"

MENU_FILE_PATH = DATA_DIR / "menu1.png"
JSON_FILES = {f.stem: f for f in (DATA_DIR).glob("*.json")}
