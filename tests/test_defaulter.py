from unittest.mock import patch

import pandas as pd
import pytest

from src.defaulter import _search_bodies, default


@pytest.fixture
def settings():
  return {
    "body": {
      "id": None,
      "fields": {
        "object_type": "asteroid",
        "critical_list_numbered_object": None,
        "limit": 1,
        "family": None,
        "orbit_uncertainty": None,
        "state": ["is_provisional"]
      }
    },
    "database": None,
    "epoch": None,
    "observer": {
      "code": None,
      "coord": None
    },
    "limit_magnitude": None,
    "exposition_time": None,
    "ADS_key": None
  }

# Test default values
def test_default_values(settings):
  result = default(settings)
  
  assert result['limit_magnitude'] == 16
  assert result['exposition_time'] == 5
  assert result['database'] == ['JPL', 'MPC']
  assert result['observer']['code'] == "geo"
  
# Test choosing values
def test_existing_values_are_preserved(settings):
  settings['limit_magnitude'] = 18
  settings['exposition_time'] = 10
  settings['database'] = ['MPC']
  settings['observer']['code'] = 'G37'

  result = default(settings)

  assert result['limit_magnitude'] == 18
  assert result['exposition_time'] == 10
  assert result['database'] == ['MPC']
  assert result['observer']['code'] == 'G37'

# Test default body ids
def test_default_body_ids(settings):

  # We use a mock to simulate a list of asteroids instead of relying in the local database or other functions
  with patch("src.defaulter._search_bodies", return_value=["Ceres", "Vesta"]):
    result = default(settings)

  assert result["body"]["id"] == ["Ceres", "Vesta"]


# Test family filtering from database
def test_search_bodies_family():

  # Fake database for testing
  fake_database = pd.DataFrame({
    "designation": ["Ceres", "Vesta", "Eris"],
    "is_mba": [True, True, False],
    "is_neo": [False, False, False],
    "is_provisional": [False, False, True],
    "is_numbered": [True, True, False],
    "orbit_uncertainty": [0, 1, 2],
  })

  # Fields for testing
  fields = {
    "object_type": "asteroid",
    "family": ["is_mba"],
    "state": ["is_numbered"],
    "orbit_uncertainty": [0, 1],
    "limit": 2,
  }

  # Use a mock to test search bodies individually without relying on local database
  with patch("src.defaulter.get_localdatabase", return_value=fake_database):
    result = _search_bodies(fields)

  # We expect only two asteroids as there are only two mbas
  assert len(result) == 2
  
  # The asteroids must be Ceres and Vesta in this situation
  assert set(result) == {"Ceres", "Vesta"}
  
# Test limit parameter in body search
def test_search_bodies_limit():

  # Database for testing
  fake_database = pd.DataFrame({
    "designation": ["Ceres", "Vesta"],
    "is_mba": [True, True],
    "is_numbered": [True, True],
    "orbit_uncertainty": [0, 0],
  })

  # Fields for testing
  fields = {
    "object_type": "asteroid",
    "family": ["is_mba"],
    "state": ["is_numbered"],
    "orbit_uncertainty": [0],
    "limit": 1,
  }

  # Use a mock to not depend on local data
  with patch("src.defaulter.get_localdatabase", return_value=fake_database):
    result = _search_bodies(fields)

  # Because of limit = 1, we expect only one result
  assert len(result) == 1
  
  # The result can be either one of the two possibilities because it chooses randomly
  assert result[0] in ["Ceres", "Vesta"]

# Test case where the limit is bigger than the amount of candidates found
def test_search_bodies_limit_greater_than_candidates():

  # Database and fields for testing
  fake_database = pd.DataFrame({
    "designation": ["Ceres", "Vesta"],
    "is_mba": [True, True],
    "is_numbered": [True, True],
    "orbit_uncertainty": [0, 0],
  })
  fields = {
    "object_type": "asteroid",
    "family": ["is_mba"],
    "state": ["is_numbered"],
    "orbit_uncertainty": [0],
    "limit": 10,
  }

  # Use a mock to test body searching without depending on local data
  with patch("src.defaulter.get_localdatabase", return_value=fake_database):
    result = _search_bodies(fields)

  # If the amount of candidates is lower than the limit, it must return all candidates
  assert len(result) == 2
  assert set(result) == {"Ceres", "Vesta"}

# Test case with no candidates
def test_search_bodies_no_candidates():

  # Database and fields for testing
  fake_database = pd.DataFrame({
    "designation": ["Ceres", "Vesta"],
    "is_neo": [False, False],
    "is_numbered": [True, True],
    "orbit_uncertainty": [0, 0],
  })
  fields = {
    "object_type": "asteroid",
    "family": ["is_neo"],
    "state": ["is_numbered"],
    "orbit_uncertainty": [0],
    "limit": 10,
  }

  # Use a mock to not depend on local data
  with patch("src.defaulter.get_localdatabase", return_value=fake_database):
    result = _search_bodies(fields)

  assert result == []