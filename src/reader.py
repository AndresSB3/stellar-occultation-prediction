import json
from pathlib import Path

# Function to read the JSON settings file
def get_config():
  
  # Get settings' directory
  src_dir = Path(__file__).resolve().parent
  root_dir = src_dir.parent
  settings_dir = root_dir / "config" / "settings.json"

  # Open JSON file
  with open(settings_dir, "r") as file:
      settings = json.load(file)
  return settings