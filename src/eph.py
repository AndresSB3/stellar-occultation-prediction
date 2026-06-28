from astropy.time import Time
from astroquery.mpc import MPC
from astroquery.jplhorizons import Horizons

# Function to get ephemerides from MPC
def mpc_eph(settings):
  
  # Extract body and epoch info from settings
  body = settings['body']['id']
  if settings['epoch']['range']:
    epoch = settings['epoch']['range']
  else:
    epoch = settings['epoch']
  
  # Get ephemerides
  eph = MPC.get_ephemeris(body, start=epoch['start'], step=epoch['step'], number=epoch['number'])
  eph['Date_jd'] = Time(eph['Date']).jd1 # date must be in JD
  
  # Extract important fields
  data = eph['Date_jd', 'RA', 'Dec', 'Delta']
  error = eph['Uncertainty 3sig', 'Unc. P.A.']
  
  # Convert to dataframe
  df = data.to_pandas()
  
  # Return data and error
  return df, error

# Function to get ephemerides from JPL
def jpl_eph(settings):
  
  # Extract body and epoch info from settings
  body = settings['body']['id']
  if settings['epoch']['range']:
    epoch = settings['epoch']['range']
  else:
    epoch = settings['epoch']
  
  # Get ephemerides
  body = Horizons(id=body, epochs=epoch)
  eph = body.ephemerides()
  
  # Extract important fields
  data = eph['datetime_jd', 'RA', 'DEC', 'delta']
  error = eph['RA_3sigma', 'DEC_3sigma', 'SMAA_3sigma', 'SMIA_3sigma', 'Theta_3sigma']
  
  # Convert to dataframe
  df = data.to_pandas()
  
  # Return data and error
  return df, error