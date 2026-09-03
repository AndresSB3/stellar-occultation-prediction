import re
import time

from astropy.time import Time
from astroquery.jplhorizons import Horizons
from astroquery.mpc import MPC


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
  error = None
  
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
    error = None
  
  # Convert to dataframe
  df = data.to_pandas()
  
  # Return data and error
  return df, error

# Function to handle ephemerides retrieval based on settings
def get_eph(body, epoch, database, verbose=False):

  # JPL case
  if "JPL" in database:
    try:
      eph, err = jpl_eph(body, epoch)
      if verbose:
        print(f'JPL query successful for {body}!')
    except Exception as e:
      if "MPC" in database:
        if verbose:
          print(f'JPL query failed. Presenting error:\n{e}\n\nQuerying MPC for {body}, wait a moment...')
        try:
          eph, err = mpc_eph(body, epoch)
          if verbose:
            print(f'MPC query successful for {body}!')
        except Exception as e:
          if verbose:
            print(f'MPC query failed. Presenting error:\n{e}\n\n')
      else:
        if verbose:
          print('JPL query failed.')
  else:
    try:
      eph, err = mpc_eph(body, epoch)
      if verbose:
        print(f'MPC query successful for {body}!')
    except Exception as e:
      if verbose:
        print(f'MPC query failed. Presenting error:\n{e}\n\n')
  
  print('Currently waiting to continue...')
  time.sleep(2)
  
  return eph, err