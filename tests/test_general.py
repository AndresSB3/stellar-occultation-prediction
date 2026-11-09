
from unittest.mock import MagicMock, call, patch

from occultations.core.general import run


def run_with_mocks(settings):

  # Use mocks to avoid external functions and file creation
  with \
    patch("occultations.core.general.get_eph", return_value="fake_eph") as mock_eph, \
    patch("occultations.core.general.EphemTable") as mock_table, \
    patch("occultations.core.general.Body") as mock_body, \
    patch("occultations.core.general.handle_diameter", return_value=100) as mock_diameter, \
    patch("occultations.core.general.get_topocentric_predictions") as mock_pred:
      
    # Configure EphemTable mock
    mock_table.return_value.table.to_pandas.return_value = MagicMock()
    
    # Run general function
    run(settings)

  # Mock CSV saving
  mock_csv = mock_table.return_value.table.to_pandas.return_value.to_csv

  return mock_eph, mock_table, mock_body, mock_diameter, mock_pred, mock_csv

# Test run with one observer and one body
def test_run_single_observer_single_id():

  # Fake settings
  fake_settings = {
    "body": {"id": ["Ceres"]},
    "epoch": {
      "start": "2026-09-09 00:00:00",
      "stop": "2026-09-09 01:00:00"
    },
    "database": "example_database",
    "ADS_key": "1234567890",
    "observer": ["500"],
    "limit_magnitude": "example_limit_magnitude"
  }

  # Run with mocks
  mock_eph, mock_table, mock_body, mock_diameter, mock_pred, mock_csv = run_with_mocks(fake_settings)

  # Every function must be called once
  mock_body.assert_called_once_with("Ceres")
  mock_diameter.assert_called_once_with(mock_body.return_value, "1234567890")
  mock_eph.assert_called_once_with(
    "Ceres",
    fake_settings["epoch"],
    "example_database",
    "500",
    verbose=False
  )
  mock_table.assert_called_once_with("fake_eph")
  mock_pred.assert_called_once_with(
    eph=mock_table.return_value, 
    epoch=fake_settings["epoch"], 
    obs="500", 
    diameter=100, 
    limit_magnitude=fake_settings["limit_magnitude"], 
    verbose=False
  )

  # Verify CSV filename
  mock_csv.assert_called_once_with(
    "output/Ceres(500)(2026-09-09 00:00:00-2026-09-09 01:00:00).csv",
    index=False
  )

# Test run with one observer and multiple bodies
def test_run_multiple_ids():

  # Fake settings
  fake_settings = {
    "body": {"id": ["Ceres", "Phoebe", "Arrokoth"]},
    "epoch": {
      "start": "2026-09-09 00:00:00",
      "stop": "2026-09-09 01:00:00"
    },
    "database": "example_database",
    "ADS_key": "1234567890",
    "observer": ["500"],
    "limit_magnitude": "example_limit_magnitude"
  }

  # Run with mocks
  mock_eph, mock_table, mock_body, mock_diameter, mock_pred, mock_csv = run_with_mocks(fake_settings)

  # Every function must be called three times
  assert mock_body.call_count == 3
  assert mock_diameter.call_count == 3
  assert mock_eph.call_count == 3
  assert mock_table.call_count == 3
  assert mock_pred.call_count == 3
  assert mock_csv.call_count == 3

  # Verify body instantiation
  mock_body.assert_has_calls([
    call("Ceres"),
    call("Phoebe"),
    call("Arrokoth"),
  ])

  # Verify ephemerides extraction
  mock_eph.assert_has_calls([
    call("Ceres", fake_settings["epoch"], "example_database", "500", verbose=False),
    call("Phoebe", fake_settings["epoch"], "example_database", "500", verbose=False),
    call("Arrokoth", fake_settings["epoch"], "example_database", "500", verbose=False),
  ])

# Test run with multiple observers and one body
def test_run_multiple_observers_single_id():

  # Fake settings
  fake_settings = {
    "body": {"id": ["Ceres"]},
    "epoch": {
      "start": "2026-09-09 00:00:00",
      "stop": "2026-09-09 01:00:00"
    },
    "database": "example_database",
    "ADS_key": "1234567890",
    "observer": ["500", "W84", "G96"],
    "limit_magnitude": "example_limit_magnitude"
  }

  # Run with mocks
  mock_eph, mock_table, mock_body, mock_diameter, mock_pred, mock_csv = run_with_mocks(fake_settings)

  # Every function must be called three times
  assert mock_body.call_count == 3
  assert mock_diameter.call_count == 3
  assert mock_eph.call_count == 3
  assert mock_table.call_count == 3
  assert mock_pred.call_count == 3
  assert mock_csv.call_count == 3

  # Verify observer calls
  mock_eph.assert_has_calls([
    call("Ceres", fake_settings["epoch"], "example_database", "500", verbose=False),
    call("Ceres", fake_settings["epoch"], "example_database", "W84", verbose=False),
    call("Ceres", fake_settings["epoch"], "example_database", "G96", verbose=False),
  ])

  # Verify CSV filenames
  mock_csv.assert_has_calls([
    call("output/Ceres(500)(2026-09-09 00:00:00-2026-09-09 01:00:00).csv", index=False),
    call("output/Ceres(W84)(2026-09-09 00:00:00-2026-09-09 01:00:00).csv", index=False),
    call("output/Ceres(G96)(2026-09-09 00:00:00-2026-09-09 01:00:00).csv", index=False),
  ])
  
# Test run with multiple observers and multiple bodies
def test_run_multiple_observers_multiple_ids():

  # Fake settings
  fake_settings = {
    "body": {"id": ["Ceres", "Phoebe"]},
    "epoch": {
      "start": "2026-09-09 00:00:00",
      "stop": "2026-09-09 01:00:00"
    },
    "database": "example_database",
    "ADS_key": "1234567890",
    "observer": ["500", "W84", "G96"],
    "limit_magnitude": "example_limit_magnitude"
  }

  # Run with mocks
  mock_eph, mock_table, mock_body, mock_diameter, mock_pred, mock_csv = run_with_mocks(fake_settings)

  # Every function must be called six times
  assert mock_body.call_count == 6
  assert mock_diameter.call_count == 6
  assert mock_eph.call_count == 6
  assert mock_table.call_count == 6
  assert mock_pred.call_count == 6
  assert mock_csv.call_count == 6

  # Verify body instantiation order
  mock_body.assert_has_calls([
    call("Ceres"),
    call("Phoebe"),
    call("Ceres"),
    call("Phoebe"),
    call("Ceres"),
    call("Phoebe"),
  ])

  # Verify ephemerides extraction order
  mock_eph.assert_has_calls([
    call("Ceres", fake_settings["epoch"], "example_database", "500", verbose=False),
    call("Phoebe", fake_settings["epoch"], "example_database", "500", verbose=False),
    call("Ceres", fake_settings["epoch"], "example_database", "W84", verbose=False),
    call("Phoebe", fake_settings["epoch"], "example_database", "W84", verbose=False),
    call("Ceres", fake_settings["epoch"], "example_database", "G96", verbose=False),
    call("Phoebe", fake_settings["epoch"], "example_database", "G96", verbose=False),
  ])

  # Verify CSV filenames
  mock_csv.assert_has_calls([
    call("output/Ceres(500)(2026-09-09 00:00:00-2026-09-09 01:00:00).csv", index=False),
    call("output/Phoebe(500)(2026-09-09 00:00:00-2026-09-09 01:00:00).csv", index=False),
    call("output/Ceres(W84)(2026-09-09 00:00:00-2026-09-09 01:00:00).csv", index=False),
    call("output/Phoebe(W84)(2026-09-09 00:00:00-2026-09-09 01:00:00).csv", index=False),
    call("output/Ceres(G96)(2026-09-09 00:00:00-2026-09-09 01:00:00).csv", index=False),
    call("output/Phoebe(G96)(2026-09-09 00:00:00-2026-09-09 01:00:00).csv", index=False),
  ])