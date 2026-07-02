import json
from pathlib import Path
import pandas as pd
import numpy as np

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

def _get_bodies():
    pass
  
def update_localdatabase():
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

  # Classify as MBAs (2.0 AU < a < 3.2 AU; e < 0.3; q > 1.3 AU)
  mba_conditions = [
    (df['semimajor_axis'] > 2.0) & 
    (df['semimajor_axis'] < 3.2) & 
    (df['eccentricity'] < 0.3) & 
    (df['perihelion_distance'] > 1.3)
  ]
  df['is_mba'] = np.select(mba_conditions, [True], default=False)

  # Classify Jupiter Trojans (4.95 AU < a < 5.45 AU; e < 0.6; I < 40°)
  jup_conditions = [
    (df['semimajor_axis'] > 4.95) &
    (df['semimajor_axis'] < 5.45) &
    (df['eccentricity'] < 0.6) &
    (df['inclination'] < 40)
  ]
  df['is_jupiter_trojan'] = np.select(jup_conditions, [True], default=False)

  # Classify centaurs (5.2 AU < a < 30 AU; I < 80°; not jupiter trojan)
  centaur_conditions = [
    (df['semimajor_axis'] > 5.2) &
    (df['semimajor_axis'] < 30) &
    (df['inclination'] < 80) &
    (~df['is_jupiter_trojan'])
  ]
  df['is_centaur'] = np.select(centaur_conditions, [True], default=False)

  # Classify TNOs (I consider classic so far: q > 1.3 AU; 41 AU < a; e < 0.25; I < 32°)
  tno_conditions = [
    (df['perihelion_distance'] > 1.3) &
    (df['semimajor_axis'] > 41) &
    (df['eccentricity'] < 0.25) &
    (df['inclination'] < 32)
  ]
  df['is_tno'] = np.select(tno_conditions, [True], default=False)

  # Others
  conditions = [
    (~df['is_neo']) &
    (~df['is_mba']) &
    (~df['is_jupiter_trojan']) &
    (~df['is_centaur']) &
    (~df['is_tno'])
  ]
  df['is_other'] = np.select(conditions, [True], default=False)

  # Separate classification dataframe
  df_classification = df[[
    'designation', 
    'is_numbered', 
    'is_provisional', 
    'orbit_uncertainty',
    'is_eccentricity_assumed',
    'has_multiple_designation',
    'is_neo',
    'is_mba',
    'is_jupiter_trojan',
    'is_centaur',
    'is_tno',
    'is_other'
  ]]

  # Write new dataframe to a csv
  df_classification.to_csv(data_dir / 'body_classification.csv', index=False)