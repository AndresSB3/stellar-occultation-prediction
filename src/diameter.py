import re

import numpy as np
from body_diameter_search import find_diameter

from local_config import get_localdatabase


# Function to check if the diameter of a SORA body class exists
def diameter_exists(body):
  return bool(body.diameter.value and not np.isnan(body.diameter.value))

# Handle diameter
def handle_diameter(body, token, verbose=False):
  if not diameter_exists(body):
    print(f'Diameter for {body.name} does not exist. Searching for diameter...')
    search_result = find_diameter([body.name], amount=500, token=token, verbose=verbose)
    if bool(search_result['Value']):
      print(f'Diameter found for {body.name}: {search_result["Value"]} km')
      body.diameter = search_result["Value"]
    else:
      print(f'Diameter not found for {body.name}, executing fallback...')
      values = get_range(body.name)
      print(f'The diameter of the object is most likely between {values[0]} and {values[1]} km.')
  else:
    print(f'Diameter for {body.name} exists: {body.diameter}')

    
def get_range(name):
  
  # Get local database
  asteroids = get_localdatabase()
  
  # Handle designation
  name = re.sub(r'(\()(.+)(\))', r'\2', name)
  
  # Specific series for given name
  series = asteroids[asteroids['designation'] == name]
  
  # Depending on orbital family, assign default range
  if series.is_neo.any():
    return (0.282, 1.188)
  elif series.is_mca.any():
    return (1.734, 3.400)
  elif series.is_mba.any():
    return (2.809, 5.778)
  elif series.is_tjn.any():
    return (12.424, 21.920)
  elif series.is_cen.any():
    return (4.280, 57.750)
  elif series.is_tno.any():
    return (15.250, 181.000)
  else: # No classification case (HYA, PAA, AST)
    return (1.439, 2.935)