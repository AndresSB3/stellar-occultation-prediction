from sora import Body

# from unc import jpl_unc, mpc_unc
from occultations.core.diameter import handle_diameter
from occultations.core.eph import get_eph
from occultations.core.ephem_table import EphemTable
from occultations.core.prediction import get_topocentric_predictions
from occultations.core.serialization import prediction_table_to_dict


def run(settings, prediction_callback=None, verbose=False):
  
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
      
      # Save ephemerides locally  
      # if isinstance(epoch, dict):
      #   if isinstance(obs, str):
      #     name = f'output/{rock}({obs})({epoch["start"]}-{epoch["stop"]}).csv'
      #   elif not obs:
      #     name = f'output/{rock}(geo)({epoch["start"]}-{epoch["stop"]}).csv'
      #   else:
      #     name = f'output/{rock}({obs.values()})({epoch["start"]}-{epoch["stop"]}).csv'
      # else:
      #   if isinstance(obs, str):
      #     name = f'output/{rock}({obs})({epoch[0]}-{epoch[-1]}).csv'
      #   elif not obs:
      #     name = f'output/{rock}(geo)({epoch[0]}-{epoch[-1]}).csv'
      #   else:
      #     name = f'output/{rock}({obs.values()})({epoch[0]}-{epoch[-1]}).csv'
        
      # eph_table.table.to_pandas().to_csv(name, index=False)
      
      # print(f'Ephemerides of {rock} were saved to output folder.')
      
      # Show diameter
      print(f"{rock}'s diameter: {diameter}")
      
      # Compute topocentric predictions for rock
      print(f'Getting predictions for {rock} from {obs} in {epoch}...')
      
      pred = get_topocentric_predictions(
        eph=eph_table, 
        epoch=epoch, 
        obs=obs, 
        diameter=diameter, 
        limit_magnitude=settings['limit_magnitude'], 
        verbose=verbose
      )
      
      # Present prediction table
      print(pred)
      
      # Check if we should send the prediction to the UI
      if prediction_callback is not None:
        
        # Serialize or convert the prediction table to a readable combination of lists and dictionaries
        pred_serial = prediction_table_to_dict(pred=pred, body=rock, obs=obs)
        
        # Send prediction callback
        prediction_callback(pred_serial)