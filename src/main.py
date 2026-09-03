from sora import Body

# from unc import jpl_unc, mpc_unc
from defaulter import default

# from eph import get_eph
from local_config import get_config, update_localdatabase


def main(verbose=False, update=False):
  
  # Updating process
  if update:
    update_localdatabase()
        
  # Get and default settings
  settings = get_config()
  settings = default(settings)
  
  # Extract body and epoch from settings
  bodies = settings['body']['id']
  # epoch = settings['epoch']
  
  # Get object ephemerides
  for rock in bodies:
    # eph, err = get_eph(rock, epoch, settings['database'], verbose=verbose)
    
    # Body instantiation
    body = Body(rock)
    
    
    
  print('Ephemerides extraction completed.')

if __name__ == "__main__":
  main(verbose=True, update=False)