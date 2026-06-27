from astroquery.mpc import MPC
from astropy.time import Time
import astropy.units as u
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


# Functions to standardize input data

# Helper function to define type object arguments
def _type_args(fields):
  args = {}
  
  # Handle provisional vs normal
  if "normal" in fields['include']:
    args['name'] = 'is_not_null'
  if "provisional" in fields['include']:
    args['designation'] = 'is_not_null'

# Helper function to search body names
def _search_bodies(fields):
  direct_args = {
    "object_type": fields['object_type'],
    "orbit_uncertainty": fields['orbit_uncertainty'],
    "critical_list_numbered_object": fields["critical_list_numbered_object"],
    "limit": fields['limit']
  }
  type_args = _type_args(fields)
  
  args = direct_args | type_args
  
  MPC.query_objects("asteroid", **args)
  
  return args

# Function to standardize input data
def default(settings):
  
  # Default values
  if not settings['limit_magnitude']:
    settings['limit_magnitude'] = 16
  if not settings['exposition_time']:
    settings['exposition_time'] = 5
  if not settings['database']:
    settings['database'] = ["JPL", "MPC"]
  if not settings['observer']['code'] and not settings['observer']['coord']:
    settings['observer']['code'] = "geocentric"
  if not settings['epoch']:
    settings['epoch'] = {
      "range": {
        "start": Time.now(),
        "stop": Time.now() + 0.5 * u.day,
        "step": "1m"
      }
    }
  if not settings['body']:
    settings['body'] = _search_bodies(settings['body']['fields'])
    
  return settings