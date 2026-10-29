import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from occultations.core.defaulter import default
from occultations.core.general import run

# Paths
STATIC_DIR = Path(__file__).parent / "static"
HTML_FILE = STATIC_DIR / "index.html"

# Initialize FastAPI application
app = FastAPI()

# Serve CSS, Javascript and other static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize home page using local html file
@app.get("/")
def home():
  return FileResponse(HTML_FILE)

# Communication with home page
@app.post("/api/config")
async def receive_config(config: dict):
  
  # Print received JSON in terminal to verify it
  print("\nConfiguration received from the browser:")
  print(json.dumps(config, indent=2, ensure_ascii=False))
  
  # Send confirmation back to javascript
  return {
    "status": "success",
    "message": "Configuration received successfully",
    "received": config
  }
  
@app.post("/api/run")
def run_pipeline(config: dict):
  
  # Default settings
  settings = default(config)
  
  # Run pipeline
  run(settings)
  
  # Confirm completion
  return {
    "status": "success",
    "message": "Ephemerides generated successfully"
  }