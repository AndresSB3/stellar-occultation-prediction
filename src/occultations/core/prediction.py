import re
from math import ceil

import numpy as np
from astropy import units as u
from astropy.time import Time
from sora.prediction import prediction


# Function to generate topocentric predictions for a given body and a given epoch
def get_topocentric_predictions(eph, epoch, obs, diameter, limit_magnitude, verbose=False):
  
  # Compute radius with diameter
  
  # Case exact value
  if isinstance(diameter, float):
    
    # Radius is half the diameter
    radius = diameter / 2
    
  # Case range of posible values
  elif isinstance(diameter, list):
    
    # Use the lower limit to only predict events that are most likely to show up
    radius = diameter[0] / 2
    
  # Case non of the above
  else:
    raise TypeError("Diameter must be a list with upper and lower ranges of possible diameters or a float value.")
  
  # Define sigma (it is 3 because of the internal errors in ephemTable)
  # sigma = 3
  
  # Extract limit magnitude from settings
  mag_lim = limit_magnitude
  
  # Compute divs and extract step (in seconds) based on epoch
  
  # Case list of UTC dates
  if isinstance(epoch, list) and isinstance(epoch[0], str):
    
    # From first date to last divided by 30 (it is already in days)
    start = Time(epoch[0])
    stop = Time(epoch[-1])
    divs = ceil(abs(stop - start).value / 30)
    
    # Smallest interval in datetime list converted to seconds
    step = np.min(np.diff(Time(epoch))).to_value("sec")
    
  # Case list of JD dates
  elif isinstance(epoch, list) and isinstance(epoch[0], float):
    
    # From first date to last divided by 30 (it is already in days)
    start = epoch[0]
    stop = epoch[-1]
    divs = ceil(abs((stop - start) / 30))
    
    # Smalles interval in julian date converted to seconds
    step = (np.min(np.diff(np.array(epoch))) * u.d).to_value("s")
    
  # Case range of dates in dictionary
  elif isinstance(epoch, dict):
    
    # Interval from start to finish divided by 30
    start = Time(epoch['start'])
    stop = Time(epoch['stop'])
    divs = ceil((abs(stop - start) / 30).value)
    
    # Handle minutes
    if re.search(r'm$', epoch['step']):
      epoch['step'] = re.sub(r'm$', 'min', epoch['step'])
      
    # Compute step converting step in epoch to seconds
    step = u.Quantity(epoch['step']).to_value(u.s)
    
  # Case non of the above
  else:
    raise TypeError("Epoch must be a dictionary with 'start' and 'stop', a list of UTC dates, or a list of Julian Dates.")
  
  # Topocentric prediction with SORA
  return prediction(
    time_beg=start,
    time_end=stop,
    ephem=eph,
    reference_center=obs,
    radius=radius,
    mag_lim=mag_lim,
    divs=divs,
    step=step,
    # sigma=sigma,
    verbose=verbose
  )