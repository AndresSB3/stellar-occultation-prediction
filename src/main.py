from local_config import update_localdatabase, get_config
from defaulter import default
from eph import jpl_eph, mpc_eph
# from unc import jpl_unc, mpc_unc
import time

def main():
    
  # Option to update
  update = True
  
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
  
  # Dictionary for testing
  ephs = {}
  errs = {}
  
  # Get object ephemerides
  for rock in body:
    if "JPL" in settings['database']:
      print(f'Querying JPL for {rock}, wait a moment...')
      try:
        eph, err = jpl_eph(rock, epoch)
        print(f'JPL query successful for {rock}!')
      except Exception as e:
        if "MPC" in settings['database']:
          print(f'JPL query failed. Presenting error:\n{e}\n\nQuerying MPC for {rock}, wait a moment...')
          try:
            eph, err = mpc_eph(rock, epoch)
            print(f'MPC query successful for {rock}!')
          except Exception as e:
            print(f'MPC query failed. Presenting error:\n{e}\n\n')
        else:
          print('JPL query failed.')
    else:
      print(f'Querying MPC for {rock}, wait a moment...')
      try:
        eph, err = mpc_eph(rock, epoch)
        print(f'MPC query successful for {rock}!')
      except Exception as e:
        print(f'MPC query failed. Presenting error:\n{e}\n\n')
    
    print('Currently waiting to continue...')
    time.sleep(2)
    ephs[rock] = eph
    errs[rock] = err
    
  print('Ephemerides extraction completed.')
  
  yes = input('Print result? (y/n)\n')
  if yes == 'y':
    print(ephs)
  else:
    print('Ok!')

if __name__ == "__main__":
  main()