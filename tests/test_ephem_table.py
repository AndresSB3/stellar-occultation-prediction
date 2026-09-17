import numpy as np
import pytest
from astropy import units as u
from astropy.table import Table

from src.ephem_table import EphemTable


# Testing table ephemerides
@pytest.fixture
def table():
  return Table({
    "time": [1, 2, 3, 4, 5] * u.d,
    "ra": [1, 2, 3, 4, 5] * u.deg,
    "dec": [1, 2, 3, 4, 5] * u.deg,
    "distance": [1, 2, 3, 4, 5] * u.au
  })

  
# The table, min_time, max_time and meta attrs must exist and have the expected values. The get_position method must exist
def test_instantiation(table):
  ephem_table = EphemTable(table)
  assert hasattr(ephem_table, 'table')
  assert (ephem_table.table == table).all()
  assert hasattr(ephem_table, 'min_time')
  assert ephem_table.min_time == table['time'].min()
  assert hasattr(ephem_table, 'max_time')
  assert ephem_table.max_time == table['time'].max()
  assert hasattr(ephem_table, 'meta')
  assert ephem_table.meta == {'kernels': 'EphemTable'}
  assert hasattr(ephem_table, 'get_position')
  assert callable(ephem_table.get_position)

# The attrs from BaseEphem must be inherited
def test_base_ephem_attrs(table):
  ephem_table = EphemTable(
    table,
    name="Test object",
    spkid="12345",
    radius=100,
    error_ra=0.5,
    error_dec=0.7,
    H=10,
    G=0.15
  )
  assert ephem_table.name == "Test object"
  assert ephem_table.spkid == "12345"
  assert ephem_table.radius == 100 * u.km
  assert ephem_table.error_ra == 0.5 * u.arcsec
  assert ephem_table.error_dec == 0.7 * u.arcsec
  assert ephem_table.H == 10
  assert ephem_table.G == 0.15

# Test instantiation errors because of lack of cols

# If table has no time, we expect an error
def test_no_time(table):
  table.remove_column("time")
  with pytest.raises(ValueError):
    EphemTable(table)

# If table has no ra, we expect an error
def test_no_ra(table):
  table.remove_column("ra")
  with pytest.raises(ValueError):
    EphemTable(table)
    
# If table has no dec, we expect an error
def test_no_dec(table):
  table.remove_column("dec")
  with pytest.raises(ValueError):
    EphemTable(table)
    
# If table has no distance, we expect an error
def test_no_distance(table):
  table.remove_column("distance")
  with pytest.raises(ValueError):
    EphemTable(table)

# If table has different names, we expect an error
def test_diff_col_names():
  table = Table({
    "date": [1, 2, 3, 4, 5],
    "RA": [1, 2, 3, 4, 5],
    "DEC": [1, 2, 3, 4, 5],
    "Delta": [1, 2, 3, 4, 5]
  })
  with pytest.raises(ValueError):
    EphemTable(table)
    
# An empty table should raise an error
def test_empty_table():
  table = Table({
    "time": [],
    "ra": [],
    "dec": [],
    "distance": []
  })
  with pytest.raises(ValueError):
    EphemTable(table)

# If the table has nans, infinites or time dups, we expect an error
def test_nans():
  table = Table({
    "time": [1, 2, 3, 4, 5] * u.d,
    "ra": [1, 2, np.nan, 4, 5] * u.deg,
    "dec": [1, 2, 3, 4, 5] * u.deg,
    "distance": [1, 2, 3, 4, 5] * u.au
  })
  with pytest.raises(ValueError):
    EphemTable(table)
def test_infs():
  table = Table({
    "time": [1, 2, 3, 4, 5] * u.d,
    "ra": [1, 2, 3, 4, 5] * u.deg,
    "dec": [1, 2, np.inf, 4, 5] * u.deg,
    "distance": [1, 2, 3, 4, 5] * u.au
  })
  with pytest.raises(ValueError):
    EphemTable(table)
def test_dups():
  table = Table({
    "time": [1, 3, 3, 4, 5] * u.d,
    "ra": [1, 2, 3, 4, 5] * u.deg,
    "dec": [1, 2, 3, 4, 5] * u.deg,
    "distance": [1, 2, 3, 4, 5] * u.au
  })
  with pytest.raises(ValueError):
    EphemTable(table)

# Impossible values must return an error
def test_negative_time():
  table = Table({
    "time": [1, 2, -3, 4, 5] * u.d,
    "ra": [1, 2, 3, 4, 5] * u.deg,
    "dec": [1, 2, 3, 4, 5] * u.deg,
    "distance": [1, 2, 3, 4, 5] * u.au
  })
  with pytest.raises(ValueError):
    EphemTable(table)
def test_negative_ra():
  table = Table({
    "time": [1, 2, 3, 4, 5] * u.d,
    "ra": [-1, 2, 3, 4, 5] * u.deg,
    "dec": [1, 2, 3, 4, 5] * u.deg,
    "distance": [1, 2, 3, 4, 5] * u.au
  })
  with pytest.raises(ValueError):
    EphemTable(table)
def test_exceed_ra():
  table = Table({
    "time": [1, 2, 3, 4, 5] * u.d,
    "ra": [1, 2, 3, 4, 361] * u.deg,
    "dec": [1, 2, 3, 4, 5] * u.deg,
    "distance": [1, 2, 3, 4, 5] * u.au
  })
  with pytest.raises(ValueError):
    EphemTable(table)
def test_exceed_dec():
  table = Table({
    "time": [1, 2, 3, 4, 5] * u.d,
    "ra": [1, 2, 3, 4, 5] * u.deg,
    "dec": [1, 2, 3, 4, 91] * u.deg,
    "distance": [1, 2, 3, 4, 5] * u.au
  })
  with pytest.raises(ValueError):
    EphemTable(table)
def test_negative_exceed_dec():
  table = Table({
    "time": [1, 2, 3, 4, 5] * u.d,
    "ra": [1, 2, 3, 4, 5] * u.deg,
    "dec": [-91, 2, 3, 4, 5] * u.deg,
    "distance": [1, 2, 3, 4, 5] * u.au
  })
  with pytest.raises(ValueError):
    EphemTable(table)
def test_negative_distance():
  table = Table({
    "time": [1, 2, 3, 4, 5] * u.d,
    "ra": [1, 2, 3, 4, 5] * u.deg,
    "dec": [1, 2, 3, 4, 5] * u.deg,
    "distance": [1, 2, 3, -4, 5] * u.au
  })
  with pytest.raises(ValueError):
    EphemTable(table)
def test_non_ascending_time():
  table = Table({
    "time": [1, 2, 4, 3, 5] * u.d,
    "ra": [1, 2, 3, 4, 5] * u.deg,
    "dec": [1, 2, 3, 4, 5] * u.deg,
    "distance": [1, 2, 3, 4, 5] * u.au
  })
  with pytest.raises(ValueError):
    EphemTable(table)

# If units are different, we expect an error, if good, we expect the attr to have the same units as the given table
def test_good_units(table):
  ephem_table = EphemTable(table)
  assert ephem_table.table["time"].unit == u.d
  assert ephem_table.table["ra"].unit == u.deg
  assert ephem_table.table["dec"].unit == u.deg
  assert ephem_table.table["distance"].unit == u.au
def test_bad_units_time(table):
  diff_time = table
  diff_time['time'].unit = u.s
  with pytest.raises(ValueError):
    EphemTable(diff_time)
def test_bad_units_ra(table):
  diff_ra = table
  diff_ra['ra'].unit = u.rad
  with pytest.raises(ValueError):
    EphemTable(diff_ra)
def test_bad_units_dec(table):
  diff_dec = table
  diff_dec['dec'].unit = u.rad
  with pytest.raises(ValueError):
    EphemTable(diff_dec)
def test_bad_units_distance(table):
  diff_distance = table
  diff_distance['distance'].unit = u.km
  with pytest.raises(ValueError):
    EphemTable(diff_distance)
    
# EphemTable must create ra_sin and ra_cos cols
def test_trig_trans(table):
  ephem_table = EphemTable(table)
  cols = ['ra_sin', 'ra_cos']
  assert all(col in ephem_table.table.columns for col in cols)
  assert all(ephem_table.table['ra_sin'] == np.sin(np.deg2rad(table['ra'])))
  assert all(ephem_table.table['ra_cos'] == np.cos(np.deg2rad(table['ra'])))