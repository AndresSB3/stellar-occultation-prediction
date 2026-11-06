from sora import Body

# from unc import jpl_unc, mpc_unc
from occultations.core.diameter import handle_diameter
from occultations.core.eph import get_eph
from occultations.core.ephem_table import EphemTable


def run(settings, verbose=False):
  
  # Extract settings data
  bodies = settings['body']['id']
  epoch = settings['epoch']
  database = settings['database']
  observer = settings['observer']
  
  # Loop through each observer
  for obs in observer:
    
    if verbose:
      print(f"Running for observer '{obs}'...")
  
    # Loop through each body for each observer
    for rock in bodies:
      
      if verbose:
        print(f"Generating ephemerides for {rock}...")
      
      # Get ephemerides and its error from the corresponding database
      eph = get_eph(rock, epoch, database, obs, verbose=verbose)
      
      # Instantiate ephemerides to EphemTable
      eph_table = EphemTable(eph)
      
      # Body instantiation
      body = Body(rock)
      
      # Check if it has a diameter
      diameter = handle_diameter(body, settings['ADS_key'])
      
      print(f'Ephemerides extraction completed for {rock}.')
        
      if isinstance(epoch, dict):
        if isinstance(obs, str):
          name = f'output/{rock}({obs})({epoch["start"]}-{epoch["stop"]}).csv'
        elif not obs:
          name = f'output/{rock}(geo)({epoch["start"]}-{epoch["stop"]}).csv'
        else:
          name = f'output/{rock}({obs.values()})({epoch["start"]}-{epoch["stop"]}).csv'
      else:
        if isinstance(obs, str):
          name = f'output/{rock}({obs})({epoch[0]}-{epoch[-1]}).csv'
        elif not obs:
          name = f'output/{rock}(geo)({epoch[0]}-{epoch[-1]}).csv'
        else:
          name = f'output/{rock}({obs.values()})({epoch[0]}-{epoch[-1]}).csv'
        
      eph_table.table.to_pandas().to_csv(name, index=False)
      
      print(f'Ephemerides of {rock} were saved to output folder.')
      
      print(f"{rock}'s diameter: {diameter}")