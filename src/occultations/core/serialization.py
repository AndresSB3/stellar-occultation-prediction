from math import isfinite


# Helper function to serialize values into a JSON-compatible format
def _serialize_values(column, index):
  
  # Extract value from the column
  value = column[index]
  
  # If it is a quantity, extract the value
  if hasattr(value, "to_value"):
    value = value.to_value(column.unit)
    
  # Make sure the value is a standard python float number
  value = float(value)
  
  # If the value is nan, convert to None for consistency in JSON formats
  return value if isfinite(value) else None

# Function to serialize the prediction table
def prediction_table_to_dict(pred, body, obs):
  
  # Container for events
  events = []
  
  # Loop through events and save their information using the helper functions
  for i in range(len(pred)):
    events.append({
      "star_id": str(pred["GaiaDR3 Source ID"][i]),     # Star ID is converted into a string
      "epoch": pred["Epoch"][i].utc.isot,               # Extract date from Time object in isot format
      "ca": _serialize_values(pred["C/A"], i),          # Use helper function to extract the quantity values of the rest as a float numbers
      "pa": _serialize_values(pred["P/A"], i),      
      "vel": _serialize_values(pred["Vel"], i),
      "g": _serialize_values(pred["G"], i)
    })
  
  # Return dictionary with meta data and event data for fetching
  return {
    "prediction_type": "topocentric",
    "object": str(body),
    "observer": obs,
    "events": events
  }