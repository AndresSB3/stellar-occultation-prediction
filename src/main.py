from local_config import update_localdatabase, get_config
from defaulter import default
from eph import jpl_eph, mpc_eph
import time

def main():
    
  # Option to update
  update = False
  
  # Updating process
  if update:
    update_localdatabase()
        
  # Get settings
  settings = get_config()
    
  # Default settings
  settings = default(settings)
  
  # Extract body and epoch
  body = settings['body']['id']
  epoch = settings['epoch']
  
  # Identify whether it is one body or multiple
  if not isinstance(body, list):
    body = [body]
  
  # Get object ephemerides
  for rock in body:
    if "JPL" in settings['database']:
      try:
        eph, err = jpl_eph(rock, epoch)
      except:  # noqa: E722
        if "MPC" in settings['database']:
          try:
            eph, err = mpc_eph(rock, epoch)
          except:  # noqa: E722
            print('There has been an error querying JPL and MPC ephemerides')
        else:
          print('There has been an error querying JPL ephemerides')
    else:
      try:
        eph, err = mpc_eph(rock, epoch)
      except:  # noqa: E722
        print('There has been an error querying MPC ephemerides')
    
    time.sleep(1)
    
  print(eph)
    

if __name__ == "__main__":
  main()