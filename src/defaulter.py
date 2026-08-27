import astropy.units as u
from astropy.time import Time

from local_config import get_localdatabase

# Functions to standardize input data

# Helper function to search body names
def _search_bodies(fields):
  
  # Default direct options
  obj_type = fields['object_type'] or 'asteroid'
  
  if obj_type == 'asteroid':
    asteroids = get_localdatabase()
    
    families = fields['family'] or ['is_neo', 'is_mca', 'is_mba', 'is_tjn', 'is_cen', 'is_tno', 'is_paa', 'is_hya', 'is_ast']
    states = fields['state'] or ['is_provisional', 'is_numbered']
    obj_unc = fields['orbit_uncertainty'] or asteroids['orbit_uncertainty'].unique()
    limit = fields['limit'] or 300
    
    asteroids = asteroids[
      asteroids[families].any(axis=1) &
      asteroids[states].any(axis=1) &
      asteroids['orbit_uncertainty'].isin(obj_unc)
    ]['designation']
      
    if not asteroids.empty:
      asteroids = asteroids.sample(n=limit).to_list()
      
    return asteroids

# Function to standardize input data
def default(settings):
  
  # Default values
  if not settings['limit_magnitude']:
    settings['limit_magnitude'] = 16
  if not settings['exposition_time']:
    settings['exposition_time'] = 5
  if not settings['database']:
    settings['database'] = ["JPL", "MPC"]
  elif not isinstance(settings['database'], list):
    settings['database'] = [settings['database']]
  if not settings['observer']['code'] and not settings['observer']['coord']:
    settings['observer']['code'] = "geo"
  if not settings['epoch']:
    settings['epoch'] = {
      "start": str(Time.now()),
      "stop": str(Time.now() + 1 * u.day),
      "step": "1m",
      "number": 720
    }
  if not settings['body']['id']:
    settings['body']['id'] = _search_bodies(settings['body']['fields'])
  elif not isinstance(settings['body']['id'], list):
    settings['body']['id'] = [settings['body']['id']]
    
  return settings