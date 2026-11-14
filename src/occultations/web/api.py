import asyncio
import json
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from occultations.core.defaulter import default
from occultations.core.general import run

''' GENERAL CONFIGURATIONS '''

# Dictionary to save the information of each session
RUNS = {}

# Lock the previous dictionary to prevent multiple threads from altering it at the same time
RUNS_LOCK = threading.Lock()

# Initialize paths for both the index.html file and the static folder
STATIC_DIR = Path(__file__).parent / "static"
HTML_FILE = STATIC_DIR / "index.html"

# Initialize FastAPI application
app = FastAPI()

# Mount the static folder to allow FastAPI to use its files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


''' FASTAPI FUNCTIONS '''

# Initialize home page using local HTML file
@app.get("/")
def home():
  return FileResponse(HTML_FILE)

# Debug function to check if the inputs of the user were parsed and received correctly
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

# Main asyncronic function
@app.post("/api/run")
async def run_pipeline(config: dict):
  
  # Default settings
  settings = default(config)
  
  # Create a unique identifier for this session
  run_id = uuid.uuid4().hex
  
  # Create a queue to store and communicate results to the GUI
  queue = asyncio.Queue()
  
  # Store information about the current session
  RUNS[run_id] = {
    "queue": queue,
    "predictions": {},
    "event_lookup": {},
    "status": "running",
    "task": None
  }
  
  # Get current event loop
  loop = asyncio.get_running_loop()
  
  # Internal function to execute in the background thread
  def execute_pipeline():
    try:
      
      # Internal function for callback called after each object-observer prediction
      def prediction_callback(result):
        
        print("API callback received a prediction!")
        
        # Extract data in JSON friendly format and as a SORA PredictionTable
        data = result["data"]
        table = result["table"]
        
        # Create an identifier for the current prediction table
        prediction_id = uuid.uuid4().hex
        
        # Store the original PredictionTable
        with RUNS_LOCK:
          RUNS[run_id]["predictions"][prediction_id] = table
          
          # Associate each event with its original table and row
          for index, event in enumerate(data["events"]):
            
            # Create an identifier for the current specific prediction and save it
            event_id = f"{prediction_id}:{index}"
            event["event_id"] = event_id
            
            # Store the prediction ID and the current index
            RUNS[run_id]["event_lookup"][event_id] = {
              "prediction_id": prediction_id,
              "row_index": index
            }
        
        # Include the prediction identifier in the serialized data
        data["prediction_id"] = prediction_id
        
        # Send the serialized prediction to the results page
        loop.call_soon_threadsafe(
          queue.put_nowait,
          {
            "event": "prediction",
            "data": data
          }
        )
  
      # Run pipeline
      run(settings, prediction_callback=prediction_callback)
      
      # Notify that the pipeline has finished with both the status and the information transmitted to the GUI
      with RUNS_LOCK:
        RUNS[run_id]["status"] = "completed"
      loop.call_soon_threadsafe(
        queue.put_nowait,
        {
          "event": "complete",
          "data": {
            "message": "Ephemerides generated successfully"
          }
        }
      )
    
    except Exception as error:
      
      # Save the error
      with RUNS_LOCK:
        RUNS[run_id]["status"] = "error"
      loop.call_soon_threadsafe(
        queue.put_nowait,
        {
          "event": "error",
          "data": {
            "message": str(error),
          }
        }
      )
  
  # Start the pipeline without blocking the API
  task = asyncio.create_task(
    asyncio.to_thread(execute_pipeline)
  )
  
  RUNS[run_id]["task"] = task
  
  # Return immediately
  return {
    "status": "success",
    "message": "Pipeline started",
    "run_id": run_id
  }

# Stream predictions to the results page
@app.get("/api/runs/{run_id}/events")
async def stream_predictions(run_id: str, request: Request):
  
  # Verify that the execution exists
  if run_id not in RUNS:
    raise HTTPException(
      status_code=404,
      detail="Run not found"
    )
  
  queue = RUNS[run_id]["queue"]
  
  # Generate Server-Sent Events
  async def event_stream():
    while True:
      
      # Stop if the browser closes or disconnects
      if await request.is_disconnected():
        break
      
      # Print out the message in queue when available
      try:
        message = await asyncio.wait_for(
          queue.get(),
          timeout=15
        )
      
      # If more than 15 seconds have passed without a message, keep online services alive until a message is obtained
      except asyncio.TimeoutError:
        
        # Keep the connection alive
        yield ": keep-alive\n\n"
        continue
      
      # When a message is received, we get the type of event and create a JSON with the information
      event_type = message["event"]
      event_data = json.dumps(message["data"])
      
      # Print the event type followed by the JSON data
      yield (
        f"event: {event_type}\n"
        f"data: {event_data}\n\n"
      )
      
      # Stop after a terminal event (process finished or error)
      if event_type in ("complete", "error"):
        break
  
  # Return the SSE response progressively
  return StreamingResponse(
    event_stream(),
    media_type="text/event-stream", # Identifier of SSE
    headers={
      "Cache-Control": "no-cache",  # Do not use responses in cache
      "X-Accel-Buffering": "no"     # Do not accumulate messages
    }
  )