from sora import Body

# from unc import jpl_unc, mpc_unc
from src.defaulter import default
from src.diameter import handle_diameter
from src.eph import get_eph
from src.ephem_table import EphemTable
from src.local_config import get_config, update_localdatabase


def main(verbose=False, update=False):
  
  # Updating process
  if update:
    update_localdatabase()
        
  # Get and default settings
  settings = get_config()
  settings = default(settings)
  
  # Extract body and epoch from settings
  bodies = settings['body']['id']
  epoch = settings['epoch']
  
  # Get object ephemerides
  for rock in bodies:
    
    # Get ephemerides and its error from the corresponding database
    eph, err = get_eph(rock, epoch, settings['database'], verbose=verbose)
    
    # Instantiate ephemerides to EphemTable
    eph_table = EphemTable(eph)
    
    # Body instantiation
    body = Body(rock)
    
    # Assign ephemerides attribute from body to the eph_table object
    body.ephem = eph_table
    
    # Check if it has a diameter
    handle_diameter(body, settings['ADS_key'])
    
    
  print('Ephemerides extraction completed.')

if __name__ == "__main__":
  main(verbose=True, update=False)