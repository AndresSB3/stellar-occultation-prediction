import json
from pathlib import Path

def get_config():
  src_dir = Path(__file__).resolve().parent
  root_dir = src_dir.parent
  settings_dir = root_dir / "config" / "settings.json"

  with open(settings_dir, "r") as file:
      settings = json.load(file)

  return settings