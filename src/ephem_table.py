import numpy as np
from astropy import units as u
from sora.ephem.meta import BaseEphem


class EphemTable(BaseEphem):
  def __init__(self, table, name=None, spkid=None, radius=None, error_ra=0, error_dec=0, H=None, G=None, **kwargs):
    
    # Handle kwargs (compatibility with base clase BaseEphem)
    base_kwargs = kwargs.copy()
    if radius is not None:
      base_kwargs['radius'] = radius
    if H is not None:
      base_kwargs['H'] = H
    if G is not None:
      base_kwargs['G'] = G
    base_kwargs['error_ra'] = error_ra
    base_kwargs['error_dec'] = error_dec
    super().__init__(name=name, spkid=spkid, **base_kwargs)
    
    # Check if the table is empty
    if len(table) == 0:
      raise ValueError("No data found.")
    
    # Data columns necessary
    cols = ['time', 'ra', 'dec', 'distance']
    
    # Validate table columns
    for col in cols:
      
      # They must exist
      if col not in table.columns:
        raise ValueError(f"'{col}' not found in data.")
      
      # They must not contain nans or infinite values
      if not np.all(np.isfinite(table[col])):
        raise ValueError(f"'{col}' contains NaN or infinite values.")
      
    # Time must not be negative
    if table['time'].min() < 0:
      raise ValueError("Time cannot be negative")
      
    # Validate ra being between 0 and 360 degrees
    if table['ra'].min() < 0:
      raise ValueError("RA coordinates must not be negative.")
    if table['ra'].max() > 360:
      raise ValueError("RA coordinates cannot exceed 360°.")
    
    # Validate dec being between -90 and 90 degrees
    if table['dec'].min() < -90:
      raise ValueError("DEC coordinates cannot be lower than -90°.")
    if table['dec'].max() > 90:
      raise ValueError("DEC coordinates cannot exceed 90°.")
    
    # Distance must be positive
    if table['distance'].min() <= 0:
      raise ValueError("Distance cannot be negative or 0.")
    
    # The time must be in increasing order
    if not np.all(np.diff(table['time']) > 0):
      raise ValueError("Time values must be in strictly increasing order.")
  
    # Validate units
    if not table['time'].unit or table['time'].unit != u.d:
      raise ValueError("Time must be given in Julian Date (JD).")
    if not table['ra'].unit or table['ra'].unit != u.deg:
      raise ValueError("RA coordinates must be in degrees.")
    if not table['dec'].unit or table['dec'].unit != u.deg:
      raise ValueError("DEC coordinates must be in degrees.")
    if not table['distance'].unit or table['distance'].unit != u.au:
      raise ValueError("Distance must be in AU.")
    
    # Store sine and cosine of RA for circular interpolation
    table['ra_sin'] = np.sin(np.deg2rad(table['ra']))
    table['ra_cos'] = np.cos(np.deg2rad(table['ra']))
      
    # Save arg data
    self.table = table
    
    # Save starting date and ending date
    self.min_time = table['time'].min()
    self.max_time = table['time'].max()
    
    # Create meta attribute
    self.meta = {'kernels': 'EphemTable'}
    
  def get_position(self, time, observer='geocenter'):
    pass