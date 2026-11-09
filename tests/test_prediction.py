from types import SimpleNamespace
from unittest.mock import ANY, patch

import numpy as np
import pytest
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy.time import Time

from occultations.core.prediction import (
  estimate_prediction_step,
  get_topocentric_predictions,
)


# Test diameter handling
@pytest.mark.parametrize(
  "diameter, expected_radius, expected_error",
  [
    (20.0, 10.0, None),         # Case float
    (20, 10.0, None),           # Case int
    (True, None, TypeError),    # Case bool
    ((10.0, 20.0), 5.0, None),  # Case tuple
    ([10.0, 20.0], 5.0, None),  # Case list
    ("20", None, TypeError),    # Case error
  ]
)
def test_radius_computation(diameter, expected_radius, expected_error):
  
  # Fake arguments for topocentric prediction
  fake_eph = None
  fake_obs = "G37"
  fake_limit_magnitude = 15.0
  fake_epoch = {
    "start": "2025-01-01",
    "stop": "2025-01-02",
    "step": "1m"
  }

  # Mock prediction function
  with \
    patch("occultations.core.prediction.prediction") as mock_pred, \
    patch("occultations.core.prediction.Observer") as mock_obs, \
    patch("occultations.core.prediction.estimate_prediction_step", return_value=10) as mock_step:
    
    # Cases with errors
    if expected_error is not None:
      
      # We expect to receive the corresponding error
      with pytest.raises(expected_error):
        get_topocentric_predictions(
          eph=fake_eph,
          epoch=fake_epoch,
          obs=fake_obs,
          diameter=diameter,
          limit_magnitude=fake_limit_magnitude
        )
        
      # Prediction, Observer and step computation must not be called because of error
      mock_pred.assert_not_called()
      mock_obs.assert_not_called()
      mock_step.assert_not_called()
  
    # Cases with no errors
    else:
      get_topocentric_predictions(
        eph=fake_eph,
        epoch=fake_epoch,
        obs=fake_obs,
        diameter=diameter,
        limit_magnitude=fake_limit_magnitude
      )
      
      # Observer must be called once
      mock_obs.assert_called_once_with(code=fake_obs)
      
      # Step computation must be called once
      mock_step.assert_called_once_with(
        eph=fake_eph,
        radius=expected_radius
      )
      
      # Prediction must be called once
      mock_pred.assert_called_once_with(
        time_beg=ANY,
        time_end=ANY,
        ephem=fake_eph,
        reference_center=ANY,
        radius=expected_radius,
        mag_lim=fake_limit_magnitude,
        divs=ANY,
        step=ANY,
        sigma=3,
        verbose=False
      )

# Test start, stop, steps, and divs computation
@pytest.mark.parametrize(
  "epoch, expected_start, expected_stop, expected_divs, expected_error",
  [
    (["2025-01-01", "2025-01-02", "2025-01-03"], Time("2025-01-01"), Time("2025-01-03"), 1, None),
    (["2025-01-02", "2025-02-08", "2025-02-10"], Time("2025-01-02"), Time("2025-02-10"), 2, None),
    ([10, 11, 12], 10, 12, 1, None),
    ([12, 20, 120], 12, 120, 4, None),
    ({"start": "2025-01-01", "stop": "2025-01-03", "step": "1m"}, Time("2025-01-01"), Time("2025-01-03"), 1, None),
    ({"start": "2025-01-01", "stop": "2025-01-03", "step": "1min"}, Time("2025-01-01"), Time("2025-01-03"), 1, None),
    ({"start": "2025-01-03", "stop": "2025-03-16", "step": "1h"}, Time("2025-01-03"), Time("2025-03-16"), 3, None),
    ("wrong_date", None, None, None, TypeError),
    ([True, False, True], None, None, None, TypeError), 
    ([], None, None, None, TypeError),
    ([10, True, 12], None, None, None, TypeError),
  ]
)
def test_epoch_computation(epoch, expected_start, expected_stop, expected_divs, expected_error):
  
  # Fake arguments for topocentric prediction
  fake_eph = None
  fake_obs = "G37"
  fake_limit_magnitude = 15.0
  fake_diameter = 10
  
  # Mock prediction
  with \
    patch("occultations.core.prediction.prediction") as mock_pred, \
    patch("occultations.core.prediction.Observer") as mock_obs, \
    patch("occultations.core.prediction.estimate_prediction_step", return_value=10) as mock_step:
    
    # Cases with errors
    if expected_error is not None:
      
      # We expect the corresponding error
      with pytest.raises(expected_error):
        get_topocentric_predictions(
          eph=fake_eph,
          epoch=epoch,
          obs=fake_obs,
          diameter=fake_diameter,
          limit_magnitude=fake_limit_magnitude
        )
        
      # Prediction, Observer and step computation must not be called
      mock_pred.assert_not_called()
      mock_obs.assert_not_called()
      mock_step.assert_not_called()
      
    # Cases without errors
    else:
      get_topocentric_predictions(
        eph=fake_eph,
        epoch=epoch,
        obs=fake_obs,
        diameter=fake_diameter,
        limit_magnitude=fake_limit_magnitude
      )
      
      # Observer must be called once
      mock_obs.assert_called_once_with(code=fake_obs)
      
      # Step computation must be called once
      mock_step.assert_called_once_with(
        eph=fake_eph,
        radius=ANY
      )
      
      # Prediction must be called once
      mock_pred.assert_called_once_with(
        time_beg=expected_start,
        time_end=expected_stop,
        ephem=fake_eph,
        reference_center=ANY,
        radius=ANY,
        mag_lim=fake_limit_magnitude,
        divs=expected_divs,
        step=ANY,
        sigma=3,
        verbose=False
      )
      
# Test observer handling
@pytest.mark.parametrize(
  "observer, is_code, expected_error",
  [
    ("G37", True, None),
    ({"lon": 10, "lat": 10, "elevation": 2}, False, None),
    (None, False, TypeError),
    ({"otherKey": 10, "lon": 10}, False, TypeError),
    ({"lon": 10, "lat": True, "elevation": 2}, False, TypeError),
    ({"lon": 10.0, "lat": 10.0, "elevation": 2.0}, False, None),
    ({"lon": 10, "lat": "10", "elevation": 2}, False, TypeError),
    (123, False, TypeError)
  ]
)
def test_observer_instantiation(observer, is_code, expected_error):
  
  # Fake arguments for topocentric prediction
  fake_eph = None
  fake_limit_magnitude = 15.0
  fake_diameter = 10
  fake_epoch = {
    "start": "2025-01-01",
    "stop": "2025-01-02",
    "step": "1m"
  }
  
  with \
    patch("occultations.core.prediction.prediction") as mock_pred, \
    patch("occultations.core.prediction.Observer", return_value="Observer Object") as mock_obs, \
    patch("occultations.core.prediction.estimate_prediction_step", return_value=10) as mock_step:
      
      # Cases with errors
      if expected_error is not None:
        
        # We expect the corresponding error
        with pytest.raises(expected_error):
          get_topocentric_predictions(
            eph=fake_eph,
            epoch=fake_epoch,
            obs=observer,
            diameter=fake_diameter,
            limit_magnitude=fake_limit_magnitude
          )
          
        # Prediction, observer and step computation must not be called
        mock_pred.assert_not_called()
        mock_obs.assert_not_called()
        mock_step.assert_not_called()
        
      # Cases without errors
      else:
        get_topocentric_predictions(
          eph=fake_eph,
          epoch=fake_epoch,
          obs=observer,
          diameter=fake_diameter,
          limit_magnitude=fake_limit_magnitude
        )
        
        # Observer must be called once
        if is_code:
          mock_obs.assert_called_once_with(code=observer)
        else:
          mock_obs.assert_called_once_with(
            lon=observer['lon'], 
            lat=observer['lat'], 
            height=observer['elevation']
          )
        
        # Step computation must be called once
        mock_step.assert_called_once_with(
          eph=fake_eph,
          radius=5
        )
        
        # Prediction must be called once
        mock_pred.assert_called_once_with(
          time_beg=ANY,
          time_end=ANY,
          ephem=fake_eph,
          reference_center="Observer Object",
          radius=ANY,
          mag_lim=fake_limit_magnitude,
          divs=ANY,
          step=ANY,
          sigma=3,
          verbose=False
        )

# Test step computation function

# Helper function to create a fake ephemeris
def create_fake_ephemeris(ra, distance):

  # Create ephemeris table
  table = Table()
  table['time'] = np.array([2460676, 2460677, 2460678]) * u.d
  table['distance'] = np.array(distance) * u.km

  # Create sky coordinates
  positions = SkyCoord(
    ra=np.array(ra) * u.deg,
    dec=np.zeros(len(ra)) * u.deg,
    frame='icrs'
  )

  # Create fake ephemeris object
  eph = SimpleNamespace(
    table=table,
    get_position=lambda time: positions
  )

  return eph


# Test prediction step computation
def test_prediction_step_computation():

  # Create fake ephemeris with constant angular velocity
  eph = create_fake_ephemeris(
    ra=[0, 1, 2],
    distance=[1000, 1000, 1000]
  )

  radius = 1
  safety = 0.5

  # Compute prediction step
  step = estimate_prediction_step(eph, radius, safety)

  # Expected angular velocity: 1 degree per day
  angular_velocity = np.deg2rad(1) / 86400

  # Expected angular radius
  angular_radius = np.arcsin(radius / 1000)

  # Expected prediction step
  expected_step = safety * 2 * angular_radius / angular_velocity

  assert step == pytest.approx(expected_step)


# Test maximum angular velocity is used
def test_prediction_step_max_angular_velocity():

  # Create fake ephemeris with variable angular velocity
  eph = create_fake_ephemeris(
    ra=[0, 1, 3],
    distance=[1000, 1000, 1000]
  )

  radius = 1

  step = estimate_prediction_step(eph, radius)

  # Maximum angular velocity: 2 degrees per day
  angular_velocity = np.deg2rad(2) / 86400

  angular_radius = np.arcsin(radius / 1000)

  expected_step = 0.5 * 2 * angular_radius / angular_velocity

  assert step == pytest.approx(expected_step)


# Test minimum angular radius is used
def test_prediction_step_minimum_angular_radius():

  # Create fake ephemeris with variable distance
  eph = create_fake_ephemeris(
    ra=[0, 1, 2],
    distance=[1000, 2000, 3000]
  )

  radius = 1

  step = estimate_prediction_step(eph, radius)

  # Minimum angular radius corresponds to maximum distance
  angular_radius = np.arcsin(radius / 3000)

  angular_velocity = np.deg2rad(1) / 86400

  expected_step = 0.5 * 2 * angular_radius / angular_velocity

  assert step == pytest.approx(expected_step)


# Test safety parameter
@pytest.mark.parametrize(
  "safety",
  [
    0.25,
    0.5,
    1.0
  ]
)
def test_prediction_step_safety(safety):

  eph = create_fake_ephemeris(
    ra=[0, 1, 2],
    distance=[1000, 1000, 1000]
  )

  radius = 1

  step = estimate_prediction_step(eph, radius, safety)

  angular_velocity = np.deg2rad(1) / 86400
  angular_radius = np.arcsin(radius / 1000)

  expected_step = safety * 2 * angular_radius / angular_velocity

  assert step == pytest.approx(expected_step)


# Test zero angular velocity
def test_prediction_step_zero_angular_velocity():

  eph = create_fake_ephemeris(
    ra=[10, 10, 10],
    distance=[1000, 1000, 1000]
  )

  with pytest.raises(
    ValueError,
    match="zero angular velocity"
  ):
    estimate_prediction_step(eph, radius=1)
