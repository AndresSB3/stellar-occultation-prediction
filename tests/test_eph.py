from unittest.mock import patch

import numpy as np
from astropy.table import MaskedColumn, Table
from astropy.time import Time

from src.eph import get_eph, jpl_eph, mpc_eph


# Test if the "m" formatting will be converted to "min"
def test_mpc_eph_step_minutes():

  # Testing epoch and fake eph
  epoch = {
    "start": "2026-09-09 00:00:00",
    "step": "1m",
    "number": 10
  }
  fake_eph = Table({
    "Date": ["2026-09-09 00:00:00"],
    "RA": [100.0],
    "Dec": [20.0],
    "Delta": [1.0],
  })

  # Use mock to not depend on queries of external databases
  with patch("src.eph.MPC.get_ephemeris", return_value=fake_eph) as mock_get_ephemeris:
    mpc_eph("Ceres", epoch)

  # Check that the get_ephemeris function was called with the following parameters ("min" format corrected)
  mock_get_ephemeris.assert_called_once_with(
    "Ceres",
    start="2026-09-09 00:00:00",
    step="1min",
    number=10
  )

# Test the correct querying of dates based on step and number
def test_mpc_eph_date_jd():

  # Testing epoch and fake eph
  epoch = {
    "start": "2026-09-09 00:00:00",
    "step": "1min",
    "number": 2
  }
  fake_eph = Table({
    "Date": [
      "2026-09-09 00:00:00",
      "2026-09-09 00:01:00",
    ],
    "RA": [100.0, 100.1],
    "Dec": [20.0, 20.1],
    "Delta": [1.0, 1.0],
  })

  # Use mock to not depend on external queries
  with patch("src.eph.MPC.get_ephemeris", return_value=fake_eph):   
    result, _ = mpc_eph("Ceres", epoch)

  # Convert expected result to time table from astropy
  expected = Time(fake_eph["Date"]).jd1

  # Verify the result
  np.testing.assert_allclose(result["Date_jd"], expected)
  
# Test error treatment in mpc eph when error exists
def test_mpc_eph_uncertainty_available():

  # Testing epoch and fake eph with real errors
  epoch = {
    "start": "2026-09-09 00:00:00",
    "step": "1min",
    "number": 1
  }
  fake_eph = Table({
    "Date": ["2026-09-09 00:00:00"],
    "RA": [100.0],
    "Dec": [20.0],
    "Delta": [1.0],
    "Uncertainty 3sig": [2.5],
    "Unc. P.A.": [45.0],
  })

  # Use mock to not depend on external queries
  with patch("src.eph.MPC.get_ephemeris", return_value=fake_eph):
    _, error = mpc_eph("Ceres", epoch)

  # Error must not be none
  assert error is not None
  
  # Both error columns must exist
  assert "Uncertainty 3sig" in error.colnames
  assert "Unc. P.A." in error.colnames
  
  # Both error columns must have the values from the fake eph
  assert error["Uncertainty 3sig"][0] == 2.5
  assert error["Unc. P.A."][0] == 45.0
  
# Test error treatment in mpc eph when error does not exist
def test_mpc_eph_uncertainty_unavailable():

  # Testing epoch and fake eph
  epoch = {
    "start": "2026-09-09 00:00:00",
    "step": "1min",
    "number": 1
  }
  fake_eph = Table({
    "Date": ["2026-09-09 00:00:00"],
    "RA": [100.0],
    "Dec": [20.0],
    "Delta": [1.0],
  })

  # Use mock to not depend on external queries
  with patch("src.eph.MPC.get_ephemeris", return_value=fake_eph):
    _, error = mpc_eph("Ceres", epoch)

  # The error must be None, as the fake eph did not had an error
  assert error is None
  
# Test the instantiation of the Horizons object
def test_jpl_eph():

  # Test epoch and fake eph and horizons object
  epoch = {
    "start": "2026-09-09 00:00:00",
    "stop": "2026-09-09 01:00:00",
    "step": "1m",
    "number": 2
  }
  fake_eph = Table({
    "datetime_jd": [2461293.5, 2461293.500694444],
    "RA": [100.0, 100.1],
    "DEC": [20.0, 20.1],
    "delta": [1.0, 1.0],
  })
  fake_horizons = patch(
    "src.eph.Horizons"
  )

  # Use mock to not depend on the instantiation of an object
  with fake_horizons as mock_horizons:
    mock_horizons.return_value.ephemerides.return_value = fake_eph
    _, _ = jpl_eph("Ceres", epoch)

  # Verify that the Horizons() function was called only once with the following arguments
  mock_horizons.assert_called_once_with(
    id="Ceres",
    epochs=epoch
  )

  # Use the fake eph as the return value from ephemerides method in the horizons mock and verify it was called once with no arguments
  mock_horizons.return_value.ephemerides.assert_called_once_with()

# Test when the uncertainty is not available for JPL
def test_jpl_eph_uncertainty_unavailable():

  # Testing epoch and fake eph
  epoch = {
    "start": "2026-09-09 00:00:00",
    "stop": "2026-09-09 01:00:00",
    "step": "1m",
    "number": 2
  }
  fake_eph = Table({
    "datetime_jd": [2461293.5, 2461293.500694444],
    "RA": [100.0, 100.1],
    "DEC": [20.0, 20.1],
    "delta": [1.0, 1.0],
  })

  # Use mock to not depend on external instantiation
  with patch("src.eph.Horizons") as mock_horizons:
    
    # Use fake_eph as return value when calling the ephemerides method
    mock_horizons.return_value.ephemerides.return_value = fake_eph
    result, error = jpl_eph("Ceres", epoch)

  # The error must be None in this case
  assert error is None
  
  # The result must have only two ephs
  assert len(result) == 2
  
  # datetime_jd must remain
  np.testing.assert_array_equal(result["datetime_jd"], fake_eph["datetime_jd"])

# Test when the uncertainty is available but it is masked
def test_jpl_eph_uncertainty_masked():

  # Testing epoch and fake eph with masked errors
  epoch = {
    "start": "2026-09-09 00:00:00",
    "stop": "2026-09-09 01:00:00",
    "step": "1m",
    "number": 2
  }
  fake_eph = Table({
    "datetime_jd": [2461293.5, 2461293.500694444],
    "RA": [100.0, 100.1],
    "DEC": [20.0, 20.1],
    "delta": [1.0, 1.0],
  })
  fake_eph["RA_3sigma"] = MaskedColumn([1.0, 1.0], mask=[True, True])
  fake_eph["DEC_3sigma"] = MaskedColumn([1.0, 1.0], mask=[True, True])
  fake_eph["SMAA_3sigma"] = MaskedColumn([1.0, 1.0], mask=[True, True])
  fake_eph["SMIA_3sigma"] = MaskedColumn([1.0, 1.0], mask=[True, True])
  fake_eph["Theta_3sigma"] = MaskedColumn([1.0, 1.0], mask=[True, True])

  # Use mock to not depend on external instantiation
  with patch("src.eph.Horizons") as mock_horizons:
    
    # Use fake eph as output for mock method ephemerides()
    mock_horizons.return_value.ephemerides.return_value = fake_eph
    _, error = jpl_eph("Ceres", epoch)

  # Error must be None as it is masked
  assert error is None

# Test get_eph for the jpl only case
def test_get_eph_jpl_success():

  # Testing epoch and fake eph and err
  epoch = {
    "start": "2026-09-09 00:00:00",
    "stop": "2026-09-09 01:00:00",
    "step": "1m",
    "number": 2
  }
  fake_eph = "fake_jpl_eph"
  fake_err = "fake_jpl_error"

  # Use a mock to not depend on eph function
  with patch("src.eph.jpl_eph", return_value=(fake_eph, fake_err)) as mock_jpl, patch("src.eph.mpc_eph") as mock_mpc:
    result_eph, result_err = get_eph("Ceres", epoch, ["JPL"])

  # Verify that jpl_eph is called only once and with the following args
  mock_jpl.assert_called_once_with("Ceres", epoch)
  
  # Verify that mpc_eph was NOT called as it is not in the databases inputted
  mock_mpc.assert_not_called()

  # The returns must match the fakes
  assert result_eph == fake_eph
  assert result_err == fake_err

# Test get_eph for the jpl and mpc case (jpl failes)
def test_get_eph_jpl_fail_mpc_success():
  
  # Testing epoch and fake eph and err
  epoch = {
    "start": "2026-09-09 00:00:00",
    "stop": "2026-09-09 01:00:00",
    "step": "1m",
    "number": 2
  }
  fake_eph = "fake_mpc_eph"
  fake_err = "fake_mpc_error"
  
  # Use a mock to not depend on eph functions
  with patch("src.eph.jpl_eph", side_effect=Exception("JPL failed")) as mock_jpl, patch("src.eph.mpc_eph", return_value=(fake_eph, fake_err)) as mock_mpc:
    result_eph, result_err = get_eph("Ceres", epoch, ["JPL", "MPC"])
  
  # Verify that jpl_eph was called once
  mock_jpl.assert_called_once_with("Ceres", epoch)
  
  # Verify that mpc_eph was also called
  mock_mpc.assert_called_once_with("Ceres", epoch)
  
  # The returns must be the those of MPC
  assert result_eph == fake_eph
  assert result_err == fake_err

# Test get_eph for the mpc only case
def test_get_eph_mpc_success():
  
  # Testing epoch and fake eph and err
  epoch = {
    "start": "2026-09-09 00:00:00",
    "stop": "2026-09-09 01:00:00",
    "step": "1m",
    "number": 2
  }
  fake_eph = "fake_mpc_eph"
  fake_err = "fake_mpc_error"

  # Use a mock to not depend on eph functions
  with patch("src.eph.mpc_eph", return_value=(fake_eph, fake_err)) as mock_mpc, patch("src.eph.jpl_eph") as mock_jpl:
    result_eph, result_err = get_eph("Ceres", epoch, ["MPC"])

  # Verify that mpc_eph is called only once and with the following args
  mock_mpc.assert_called_once_with("Ceres", epoch)
  
  # Verify that jpl_eph was NOT called as it is not in the databases inputted
  mock_jpl.assert_not_called()

  # The returns must match the fakes
  assert result_eph == fake_eph
  assert result_err == fake_err
    
# Test get_eph for the jpl only case (jpl fails)
def test_get_eph_jpl_fail():
  
  # Testing epoch and fake eph and err
  epoch = {
    "start": "2026-09-09 00:00:00",
    "stop": "2026-09-09 01:00:00",
    "step": "1m",
    "number": 2
  }

  # Use a mock to not depend on eph function
  with patch("src.eph.jpl_eph", side_effect=Exception("JPL failed")) as mock_jpl, patch("src.eph.mpc_eph") as mock_mpc:
    result_eph, result_err = get_eph("Ceres", epoch, ["JPL"])

  # Verify that jpl_eph is called only once and with the following args
  mock_jpl.assert_called_once_with("Ceres", epoch)
  
  # Verify that mpc_eph was NOT called as it is not in the databases inputted
  mock_mpc.assert_not_called()

  # The returns must match the fakes
  assert result_eph is None
  assert result_err is None

# Test get_eph when both databases fail
def test_get_eph_both_fail():
  
  # Testing epoch and fake eph and err
  epoch = {
    "start": "2026-09-09 00:00:00",
    "stop": "2026-09-09 01:00:00",
    "step": "1m",
    "number": 2
  }
  
  # Use a mock to not depend on eph functions
  with patch("src.eph.jpl_eph", side_effect=Exception("JPL failed")) as mock_jpl, patch("src.eph.mpc_eph", side_effect=Exception("MPC failed")) as mock_mpc:
    result_eph, result_err = get_eph("Ceres", epoch, ["JPL", "MPC"])
  
  # Verify that both eph functions were called
  mock_mpc.assert_called_once_with("Ceres", epoch)
  mock_jpl.assert_called_once_with("Ceres", epoch)
  
  # The results must be none
  assert result_eph is None
  assert result_err is None