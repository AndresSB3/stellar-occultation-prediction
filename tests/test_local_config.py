import math
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from src.local_config import (
  _update_mpcorb,
  classify_bodies,
  get_config,
  get_localdatabase,
  update_localdatabase,
)


def test_get_config():
  settings = get_config()

  assert "body" in settings
  assert "database" in settings
  assert "observer" in settings
  
# Test correct reading of local database
def test_get_localdatabase():
  
  # Get local database (no mock needed, we are testing the local database itself)
  database = get_localdatabase()
  
  # The database must be a pandas dataframe
  assert isinstance(database, pd.DataFrame)
  
  # The following columns must exist in the dataframe
  cols = [
    "designation",
    "is_numbered", 
    "is_provisional",
    "orbit_uncertainty",
    "is_eccentricity_assumed",
    "has_multiple_designation",
    "is_neo",
    "is_mca",
    "is_mba",
    "is_tjn",
    "is_cen",
    "is_tno",
    "is_paa",
    "is_hya",
    "is_ast"
  ]
  assert set(cols).issubset(set(database.columns))
  
# Test correct classification of bodies using classify_bodies
@pytest.mark.parametrize(
  "name, U, a, e, status, unc, assumed, multiple, family",
  [
    ("(1) Example NEO", "0", 1.0, 0, "is_numbered", 0.0, False, False, "is_neo"),
    ("1958 EXMCA", "F", 1.5, 0, "is_provisional", np.nan, True, True, "is_mca"),
    ("(33) Example MBA", "E", 3.0, 0, "is_numbered", np.nan, True, False, "is_mba"),
    ("3820 EXTJN", "1", 5.0, 0.1, "is_provisional", 1.0, False, False, "is_tjn"),
    ("(40) Example CEN", "3", 21.5, 0.3, "is_numbered", 3.0, False, False, "is_cen"),
    ("2359 EXTNO", "9", 64.0, 0.8, "is_provisional", 9.0, False, False, "is_tno"),
    ("(100) Example PAA", "D", 313.0, 1, "is_numbered", np.nan, False, True, "is_paa"),
    ("9632 EXHYA", "5", 2, 1.4, "is_provisional", 5.0, False, False, "is_hya"),
    ("(333) Example AST", "6", 1.8, 0, "is_numbered", 6.0, False, False, "is_ast"),
    ("border", "", 1.3, 0, "is_provisional", np.nan, False, False, "is_ast"),
    ("border", "", 1.666, 0, "is_provisional", np.nan, False, False, "is_ast"),
    ("border", "", 3.2, 0.5, "is_provisional", np.nan, False, False, "is_ast"),
    ("border", "", 4.6, 0, "is_provisional", np.nan, False, False, "is_ast"),
    ("border", "", 5.5, 0, "is_provisional", np.nan, False, False, "is_ast"),
    ("border", "", 30.1, 0, "is_provisional", np.nan, False, False, "is_ast"),
  ]
)
def test_classify_bodies(name, U, a, e, status, unc, assumed, multiple, family):
  
  # Testing dataframe
  df = pd.DataFrame({
    "designation": [name],
    "U": [U],
    "semimajor_axis": [a],
    "eccentricity": [e]
  })
  
  # Call function
  result = classify_bodies(df)
  
  # The following columns must exist in the result
  cols = [
    "designation",
    "is_numbered", 
    "is_provisional",
    "orbit_uncertainty",
    "is_eccentricity_assumed",
    "has_multiple_designation",
    "is_neo",
    "is_mca",
    "is_mba",
    "is_tjn",
    "is_cen",
    "is_tno",
    "is_paa",
    "is_hya",
    "is_ast"
  ]
  assert set(cols).issubset(set(result.columns))
  
  # Check status
  assert result[status].iloc[0]
  
  # Check uncertainty
  assert result['is_eccentricity_assumed'].iloc[0] == assumed
  assert result['has_multiple_designation'].iloc[0] == multiple
  
  if np.isnan(unc):
    assert np.isnan(result['orbit_uncertainty'].iloc[0])
  else:
    assert math.isclose(result['orbit_uncertainty'].iloc[0], unc)
    
  # Check family
  assert result[family].iloc[0]

# Test updating of the local database using update mpcorb
def test_update_mpcorb(tmp_path):

  # Fake response from MPC
  fake_content = b"fake MPCORB data"

  # Use a mock to not request every time a test is performed and to not alter the local database
  with patch("src.local_config.requests.get") as mock_get, patch("src.local_config.data_dir", tmp_path):
    
    # Mock methods
    mock_response = mock_get.return_value
    mock_response.content = fake_content

    # Call function
    _update_mpcorb()

  # Check that the request was done once and with the following args
  mock_get.assert_called_once_with(
    "https://www.minorplanetcenter.net/iau/MPCORB/MPCORB.DAT",
    timeout=120
  )

  # Check that the status was raised once
  mock_response.raise_for_status.assert_called_once_with()

  # Check that the file was downloaded and has the fake content
  saved_file = tmp_path / "MPCORB.DAT"
  assert saved_file.exists()
  assert saved_file.read_bytes() == fake_content
  
# Test that update mpcorb wont overwrite file in case of HTTP error
def test_update_mpcorb_error(tmp_path):

  # Use a mock to not request or change local data
  with patch("src.local_config.requests.get") as mock_get, patch("src.local_config.data_dir", tmp_path):

    # Mock the method
    mock_response = mock_get.return_value

    # Simulate an HTTP error
    mock_response.raise_for_status.side_effect = Exception("HTTP error")

    # The function must propagate the exception
    with pytest.raises(Exception, match="HTTP error"):
      _update_mpcorb()

  # Check that there was an attempt to request
  mock_get.assert_called_once_with(
    "https://www.minorplanetcenter.net/iau/MPCORB/MPCORB.DAT",
    timeout=120
  )

  # Check that there was an attempt to raise for status
  mock_response.raise_for_status.assert_called_once_with()

  # Check that the file was not altered or saved
  saved_file = tmp_path / "MPCORB.DAT"
  assert not saved_file.exists()

# Test update local database when download is false
def test_update_localdatabase(tmp_path):

  # Fake directories for each directory used
  data_dir = tmp_path / "data"
  config_dir = tmp_path / "config"

  data_dir.mkdir()
  config_dir.mkdir()

  # Fake MPCORB file
  mpcorb_file = data_dir / "MPCORB.DAT"
  mpcorb_file.write_text(
      "some header\n"
      "00001 data starts here\n"
      "some data\n"
  )

  # Fake layout
  layout_file = config_dir / "mpcorb_layout.json"
  layout_file.write_text('{"colspecs": [], "names": []}')

  # Use mocks to not depend on local database and other functions
  with patch("src.local_config.data_dir", data_dir), patch("src.local_config.config_dir", config_dir), patch("src.local_config.pd.read_fwf") as mock_read_fwf, patch("src.local_config.classify_bodies") as mock_classify:

    # Fake dataframe returned by read_fwf
    fake_df = pd.DataFrame({"designation": ["Test"]})
    mock_read_fwf.return_value = fake_df

    # Fake classified dataframe
    fake_classified = pd.DataFrame({"designation": ["Test"]})
    mock_classify.return_value = fake_classified

    update_localdatabase(download=False)
  
  # Check that both the read and classify functions were called once
  mock_read_fwf.assert_called_once_with(mpcorb_file, colspecs=[], names=[], skiprows=1)
  mock_classify.assert_called_once_with(fake_df) 
  
  # Check that the local database was created
  assert (data_dir / "body_classification.csv").exists()
  
# Test update local database when download is true
def test_updatelocaldatabase_download(tmp_path):
  
  # Fake directories for each directory used
  data_dir = tmp_path / "data"
  config_dir = tmp_path / "config"

  data_dir.mkdir()
  config_dir.mkdir()

  # Fake MPCORB file
  mpcorb_file = data_dir / "MPCORB.DAT"
  mpcorb_file.write_text(
      "some header\n"
      "00001 data starts here\n"
      "some data\n"
  )

  # Fake layout
  layout_file = config_dir / "mpcorb_layout.json"
  layout_file.write_text('{"colspecs": [], "names": []}')
  
  # Use mock to not depend on update_mpcorb function
  with patch("src.local_config.data_dir", data_dir), patch("src.local_config.config_dir", config_dir), patch("src.local_config.pd.read_fwf") as mock_read_fwf, patch("src.local_config.classify_bodies") as mock_classify, patch("src.local_config._update_mpcorb") as mock_update:
    
    # Fake dataframe returned by read_fwf
    fake_df = pd.DataFrame({"designation": ["Test"]})
    mock_read_fwf.return_value = fake_df

    # Fake classified dataframe
    fake_classified = pd.DataFrame({"designation": ["Test"]})
    mock_classify.return_value = fake_classified
    
    update_localdatabase(download=True)
  
  # Check that the function was called once
  mock_update.assert_called_once_with()