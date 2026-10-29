from sora import Body

# from unc import jpl_unc, mpc_unc
from occultations.core.diameter import handle_diameter
from occultations.core.eph import get_eph
from occultations.core.ephem_table import EphemTable


def run(settings, verbose=False):
  
  # Extract body and epoch from settings
  bodies = settings['body']['id']
  epoch = settings['epoch']
  
  # Get object ephemerides
  for rock in bodies:
    
    # Get ephemerides and its error from the corresponding database
    eph = get_eph(rock, epoch, settings['database'], verbose=verbose)
    
    # Instantiate ephemerides to EphemTable
    eph_table = EphemTable(eph)
    
    # Body instantiation
    body = Body(rock)
    
    # Check if it has a diameter
    diameter = handle_diameter(body, settings['ADS_key'])
    
    
  print('Ephemerides extraction completed.')
  
  if isinstance(epoch, dict):
    name = f'output/{rock}({epoch["start"]}-{epoch["stop"]}).csv'
    eph_table.table.to_pandas().to_csv(name, index=False)
  elif isinstance(epoch, list):
    name = f'output/{rock}({epoch[0]}-{epoch[-1]}).csv'
    eph_table.table.to_pandas().to_csv(name, index=False)
  
  print('Ephemerides saved to output folder.')
  
  print(diameter)