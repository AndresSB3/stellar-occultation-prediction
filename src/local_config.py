import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests

src_dir = Path(__file__).resolve().parent
root_dir = src_dir.parent
config_dir = root_dir / "config"
data_dir = root_dir / "data"

# Function to read the JSON settings file
def get_config():
  
  # Get settings' directory
  settings_dir = config_dir / "settings.json"

  # Open JSON file
  with open(settings_dir, "r") as file:
      settings = json.load(file)
  return settings

# Function to import local classification database
def get_localdatabase():
  
  # Data directory
  dir = data_dir / "body_classification.csv"
  
  # Read CSV file
  return pd.read_csv(dir, delimiter=',')
  
# Function to automatically download MPCORB database
def _update_mpcorb():
  url = "https://www.minorplanetcenter.net/iau/MPCORB/MPCORB.DAT"

  print("Requesting MPCORB...")
  r = requests.get(url, timeout=120)
  print("Downloading MPCORB...")
  r.raise_for_status()

  Path(data_dir).write_bytes(r.content)
  print(f"File saved in {data_dir}")
  
# Function to update local classification database based on MPCORB data
def update_localdatabase(download=False):
  
  # Optional MPCORB internet updating
  if download:
    _update_mpcorb()
  
  MPCORB_dir = data_dir / "MPCORB.DAT"
  layout_dir = config_dir / "mpcorb_layout.json"
  
  with open(MPCORB_dir, "r") as f:
    for i, line in enumerate(f):
      if not line.startswith("00001"):
        continue
      header_rows = i
      break
  
  with open(layout_dir, "r") as file:
    layout = json.load(file)
  
  # Dataframe conversion
  df = pd.read_fwf(
      MPCORB_dir,
      colspecs=layout["colspecs"],
      names=layout["names"],
      skiprows=header_rows
  )
  
  # Classify as numbered or provisional (state)
  df['is_numbered'] = df['designation'].str.startswith("(")
  df['is_provisional'] = ~df['is_numbered']

  # Classify the orbit uncertainty (U)
  df['orbit_uncertainty'] = (pd.to_numeric(df['U'], errors='coerce'))
  df['is_eccentricity_assumed'] = df['U'].isin(['E', 'F'])
  df['has_multiple_designation'] = df['U'].isin(['D', 'F'])

  # Compute perihelion distance (q = a(1-e)) [AU]
  df['perihelion_distance'] = df['semimajor_axis'] * (1 - df['eccentricity'])

  # Classify as NEOs (q < 1.3 AU)
  df['is_neo'] = df['perihelion_distance'] < 1.3
  
  # Classify as MCA (SBDB: 1.3 < q < 1.666 && a < 3.2)
  mca_conditions = [
    (df['semimajor_axis'] < 3.2) &
    (df['perihelion_distance'] > 1.3) &
    (df['perihelion_distance'] < 1.666)
  ]
  df['is_mca'] = np.select(mca_conditions, [True], default=False)

  # Classify as MBAs (SBDB: 1.666 < q && 2 < a < 4.6)
  mba_conditions = [
    (df['semimajor_axis'] > 2.0) & 
    (df['semimajor_axis'] < 4.6) &
    (df['perihelion_distance'] > 1.666)
  ]
  df['is_mba'] = np.select(mba_conditions, [True], default=False)

  # Classify Jupiter Trojans (SBDB: 4.6 < a < 5.5 && e < 0.3)
  jup_conditions = [
    (df['semimajor_axis'] > 4.6) &
    (df['semimajor_axis'] < 5.5) &
    (df['eccentricity'] < 0.3)
  ]
  df['is_tjn'] = np.select(jup_conditions, [True], default=False)

  # Classify centaurs (SBDB: 5.5 < a < 30.1)
  centaur_conditions = [
    (df['semimajor_axis'] > 5.5) &
    (df['semimajor_axis'] < 30.1) &
    (~df['is_tjn'])
  ]
  df['is_cen'] = np.select(centaur_conditions, [True], default=False)

  # Classify TNOs (SBDB: 30.1 < a)
  tno_conditions = [
    (df['semimajor_axis'] > 30.1)
  ]
  df['is_tno'] = np.select(tno_conditions, [True], default=False)

  # Classify PAA (e = 1)
  df['is_paa'] = df['eccentricity'] == 1

  # Classify HYA (e > 1)
  df['is_hya'] = df['eccentricity'] > 1

  # AST (others)
  conditions = [
    (~df['is_neo']) &
    (~df['is_mca']) &
    (~df['is_mba']) &
    (~df['is_tjn']) &
    (~df['is_cen']) &
    (~df['is_tno']) &
    (~df['is_paa']) &
    (~df['is_hya'])
  ]
  df['is_ast'] = np.select(conditions, [True], default=False)

  # Separate classification dataframe
  df_classification = df[[
    'designation', 
    'is_numbered', 
    'is_provisional', 
    'orbit_uncertainty',
    'is_eccentricity_assumed',
    'has_multiple_designation',
    'is_neo',
    'is_mca',
    'is_mba',
    'is_tjn',
    'is_cen',
    'is_tno',
    'is_paa',
    'is_hya',
    'is_ast'
  ]]
  
  # Handle numbered + designation combinations
  df_classification['designation'] = df_classification['designation'].str.replace(r"\(\d+\)\s(.*)", r"\1", regex=True)

  # Write new dataframe to a csv
  df_classification.to_csv(data_dir / 'body_classification.csv', index=False)