from astropy.time import Time
from astroquery.mpc import MPC
from astroquery.jplhorizons import Horizons
import re

# Function to get ephemerides from MPC
def mpc_eph(body, epoch):
  
  # Handle minutes
  if re.search(r'm$', epoch['step']):
    epoch['step'] = re.sub(r'm$', 'min', epoch['step'])
  
  # Get ephemerides
  eph = MPC.get_ephemeris(
    body, 
    start=epoch['start'], 
    step=epoch['step'], 
    number=epoch['number']
  )
  eph['Date_jd'] = Time(eph['Date']).jd1 # date must be in JD
  
  # Extract important fields
  data = eph['Date_jd', 'RA', 'Dec', 'Delta']
  error = []
  
  # Check for uncertainty fields
  unc_cols = ['Uncertainty 3sig', 'Unc. P.A.']
  if all(col in eph.colnames for col in unc_cols):
    error = eph['Uncertainty 3sig', 'Unc. P.A.']
  else:
    print('Ephemeris uncertainty is not available.')
  
  # Convert to dataframe
  df = data.to_pandas()
  
  # Return data and error
  return df, error

# Function to get ephemerides from JPL
def jpl_eph(body, epoch):
  
  # Get ephemerides
  body = Horizons(id=body, epochs=epoch)
  eph = body.ephemerides()
  
  # Extract important fields
  data = eph['datetime_jd', 'RA', 'DEC', 'delta']
  error = eph['RA_3sigma', 'DEC_3sigma', 'SMAA_3sigma', 'SMIA_3sigma', 'Theta_3sigma']
  
  # Check if uncertainties exist
  if all(error['RA_3sigma'].mask):
    print('Uncertainty is masked, orbit solution might only be nominal and not have an uncertainty available.')
  
  # Convert to dataframe
  df = data.to_pandas()
  
  # Return data and error
  return df, error