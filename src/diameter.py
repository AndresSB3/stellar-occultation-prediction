import numpy as np
from body_diameter_search import find_diameter


# Function to check if the diameter of a SORA body class exists
def diameter_exists(body):
  return bool(body.diameter.value and not np.isnan(body.diameter.value))

# Handle diameter
def handle_diameter(body):
  if not diameter_exists(body):
    print(f'Diameter for {body.name} does not exist. Searching for diameter...')
    search_result = find_diameter(body)
    if search_result:
      print(f'Diameter found for {body.name}: {search_result} km')
      body.diameter.value = search_result
    else:
      print(f'Diameter not found for {body.name}.')
  else:
    print(f'Diameter for {body.name} exists: {body.diameter.value} km')