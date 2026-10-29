import re

import numpy as np
from body_diameter_search import find_diameter

from occultations.core.local_config import get_localdatabase


# Function to check if the diameter of a SORA body class exists
def diameter_exists(body):
  return bool(body.diameter.value and not np.isnan(body.diameter.value))

# Handle diameter
def handle_diameter(body, token, verbose=False):
  
  # Case diameter does not exist in SBDB database
  if not diameter_exists(body):
    
    # Message
    print(f'Diameter for {body.name} does not exist. Searching for diameter...')
    
    # Handle designation
    name = re.sub(r'(.+\()(.+)(\))', r'\2', body.name)
    
    # Use find_diameter tool to search for the diameter in ADS database if an ADS token is provided
    try:
      search_result = find_diameter([name], amount=500, token=token, verbose=verbose)
    except:  # noqa: E722
      print("ADS token was not provided or is invalid.")
      search_result = {"Value": None}
      
    # If a result is found return it
    if bool(search_result['Value']):
      
      # Message
      print(f'Diameter found for {name}: {search_result["Value"]} km')
      
      # Return found diameter
      body.diameter = search_result["Value"]
      return search_result
    
    # If not, execute fallback
    else:
      
      # Message
      print(f'Diameter not found for {body.name}, executing fallback...')
      
      # Assign a range of diameters based on the orbital family
      values = get_range(body.name)
      
      # Return range
      print(f'The diameter of the object is most likely between {values[0]} and {values[1]} km.')
      return values
  else:
    print(f'Diameter for {body.name} exists: {body.diameter}')
    return body.diameter.value

    
def get_range(name):
  
  # Get local database
  asteroids = get_localdatabase()
  
  # Handle designation
  name = re.sub(r'(.+\()(.+)(\))', r'\2', name)
  
  # Specific series for given name
  series = asteroids[asteroids['designation'] == name]
  
  # Depending on orbital family, assign default range
  if series.is_neo.any():
    print("The object's family is neo.")
    return (0.282, 1.188)
  elif series.is_mca.any():
    print("The object's family is mca.")
    return (1.734, 3.400)
  elif series.is_mba.any():
    print("The object's family is mba.")
    return (2.809, 5.778)
  elif series.is_tjn.any():
    print("The object's family is tjn.")
    return (12.424, 21.920)
  elif series.is_cen.any():
    print("The object's family is cen.")
    return (4.280, 57.750)
  elif series.is_tno.any():
    print("The object's family is tno.")
    return (15.250, 181.000)
  else: # No classification case (HYA, PAA, AST)
    print("The object does not have a clear family (ast).")
    return (1.439, 2.935)