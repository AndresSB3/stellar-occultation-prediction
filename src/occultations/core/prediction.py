from math import ceil

import numpy as np
from astropy import units as u
from astropy.time import Time
from sora.observer import Observer
from sora.prediction import prediction


# Function to compute prediction step based on object size and distance
def estimate_prediction_step(eph, radius, safety=0.5):

  # Extract ephemeris dates
  times = Time(eph.table['time'].value, format='jd')

  # Get positions in ephemeris dates as a skycoord object
  positions = eph.get_position(time=times)

  # Get time differences and convert them to seconds
  dt = np.diff(times.jd) * 86400

  # Compute the angular separation between each skycoord position and convert them to radians
  angular_separation = positions[:-1].separation(positions[1:]).to_value(u.rad)

  # Compute maximum angular velocity
  angular_velocity = np.max(angular_separation / dt)
  
  # Angular velocity must not be 0
  if angular_velocity == 0:
    raise ValueError("Cannot estimate prediction step: zero angular velocity.")
  

  # Compute angular radius of the object
  
  # Compute distance in kilometers
  distance = eph.table['distance'].quantity.to_value(u.km)

  # Convert radius to angular radius using the distance
  angular_radius = np.arcsin(np.clip(radius / distance, 0, 1))
  
  # Use minimum angular radius as search radius
  search_radius = np.min(angular_radius)

  # Estimate prediction step based on angular radius and angular velocity (safety parameter included)
  step = safety * 2 * search_radius / angular_velocity

  return step


# Function to generate topocentric predictions for a given body and a given epoch
def get_topocentric_predictions(eph, epoch, obs, diameter, limit_magnitude, verbose=False):
  
  # Compute radius with diameter
  
  # Case exact value
  if isinstance(diameter, (float, int)) and not isinstance(diameter, bool):
    
    # Radius is half the diameter
    radius = diameter / 2
    
  # Case range of posible values
  elif isinstance(diameter, (list, tuple)):
    
    # Use the lower limit to only predict events that are most likely to show up
    radius = diameter[0] / 2
    
  # Case none of the above
  else:
    raise TypeError("Diameter must be a list with upper and lower ranges of possible diameters or a value.")
  
  # Define sigma (it is 3 because of the internal errors in ephemTable)
  sigma = 3
  
  # Compute start, stop and divs based on epoch
  
  # Case list of UTC dates
  if (
    isinstance(epoch, list) and 
    len(epoch) > 0 and 
    all(isinstance(x, str) for x in epoch)
  ):
    
    # From first date to last divided by 30 (it is already in days)
    start = Time(epoch[0])
    stop = Time(epoch[-1])
    divs = ceil(abs(stop - start).value / 30)
    
  # Case list of JD dates
  elif (
    isinstance(epoch, list) and 
    len(epoch) > 0 and 
    all(
      isinstance(x, (float, int)) and 
      not isinstance(x, bool) 
      for x in epoch
    )
  ):
    
    # From first date to last divided by 30 (it is already in days)
    start = epoch[0]
    stop = epoch[-1]
    divs = ceil(abs((stop - start) / 30))
    
  # Case range of dates in dictionary
  elif isinstance(epoch, dict):
    
    # Interval from start to finish divided by 30
    start = Time(epoch['start'])
    stop = Time(epoch['stop'])
    divs = ceil((abs(stop - start) / 30).value)
    
  # Case non of the above
  else:
    raise TypeError("Epoch must be a dictionary with 'start' and 'stop', a list of UTC dates, or a list of Julian Dates.")
  
  # Instantiate observer with obs arg
  if isinstance(obs, str):
    reference_center = Observer(code=obs)
  elif (
    isinstance(obs, dict) and
    all(key in obs for key in ("lon", "lat", "elevation")) and
    all(
      isinstance(obs[key], (int, float)) and not isinstance(obs[key], bool)
      for key in ("lon", "lat", "elevation")
    )
  ):
    reference_center = Observer(lon=obs['lon'], lat=obs['lat'], height=obs['elevation'])
  else:
    raise TypeError("Observer must be a string with a code or a dictionary with earth coordinates.")
  
  # Compute step based on epoch
  step = estimate_prediction_step(eph=eph, radius=radius)
  
  # Topocentric prediction with SORA
  return prediction(
    time_beg=start,
    time_end=stop,
    ephem=eph,
    reference_center=reference_center,
    radius=radius,
    mag_lim=limit_magnitude,
    divs=divs,
    step=step,
    sigma=sigma,
    verbose=verbose
  )