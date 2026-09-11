from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from src.diameter import diameter_exists, get_range, handle_diameter


# Testing diameter object
class FakeDiameter:
  def __init__(self, value):
    self.value = value

# Testing body to simulate SORA body class
class FakeBody:
  def __init__(self, name, diameter):
    self.name = name
    self.diameter = FakeDiameter(diameter)

# Test if the function returns true when given a plausible diameter
def test_diameter_exists():
  assert diameter_exists(FakeBody('Ceres', 5))

# Test if the function returns false when given a nan
def test_diameter_does_not_exist_if_nan():
  assert not diameter_exists(FakeBody('Ceres', np.nan))
  
# Test if the function returns false when given a 0
def test_diameter_does_not_exist_if_zero():
  assert not diameter_exists(FakeBody('Ceres', 0))

# Test if the function returns the correct range for each orbital family
@pytest.mark.parametrize(
  "classification, expected",
  [
    ("is_neo", (0.282, 1.188)),
    ("is_mca", (1.734, 3.400)),
    ("is_mba", (2.809, 5.778)),
    ("is_tjn", (12.424, 21.920)),
    ("is_cen", (4.280, 57.750)),
    ("is_tno", (15.250, 181.000)),
    ("is_hya", (1.439, 2.935)),
    ("is_paa", (1.439, 2.935))
  ]
)
def test_get_range(classification, expected):

  # Fake database to not rely on local database
  fake_database = pd.DataFrame({
    "designation": ["Ceres"],
    "is_neo": [False],
    "is_mca": [False],
    "is_mba": [False],
    "is_tjn": [False],
    "is_cen": [False],
    "is_tno": [False],
  })

  # Activate the classification we are currently testing
  fake_database.loc[0, classification] = True

  # Use mock to not depend on local database
  with patch("src.diameter.get_localdatabase", return_value=fake_database):
    result = get_range("Ceres")

  # We expect the function to return the corresponding range depending on the orbital family
  assert result == expected

# Test default range (AST)
def test_get_range_other():

  # Database for testing
  fake_database = pd.DataFrame({
    "designation": ["Ceres"],
    "is_neo": [False],
    "is_mca": [False],
    "is_mba": [False],
    "is_tjn": [False],
    "is_cen": [False],
    "is_tno": [False],
  })

  # Mock to not depend on local database
  with patch("src.diameter.get_localdatabase", return_value=fake_database):
    result = get_range("Ceres")

  # We expect the function to return the default diameter range (HYA, PAA, AST)
  assert result == (1.439, 2.935)
  
# Test handling existing diameter
def test_handle_diameter_existing():

  # Testing body with existing diameter
  body = FakeBody("Ceres", 900)

  # Mock both the find and ranges
  with patch("src.diameter.find_diameter") as mock_find, patch("src.diameter.get_range") as mock_range:
    handle_diameter(body, token="fake_token")

  # Check that both mocks were never called, as the diameter does exist
  mock_find.assert_not_called()
  mock_range.assert_not_called()
  
# Test handling non-existing diameter and finding a search with tool
def test_handle_diameter_search_found():

  # Testing body with non-existing diameter
  body = FakeBody("Ceres", np.nan)

  # Testing search result
  search_result = {"Value": 939.4}

  # Mock the search result to not depend on the find_diameter tool
  with patch("src.diameter.find_diameter", return_value=search_result) as mock_find:
    handle_diameter(body, token="fake_token")

  # Verify that the mock was called only once
  mock_find.assert_called_once_with(["Ceres"], amount=500, token="fake_token", verbose=False)

  # Verify that the diameter was assigned to the body class
  assert body.diameter == 939.4
  
# Test handling non-existing diameter and not finding a search with tool
def test_handle_diameter_search_not_found():

  # Testing body with non-existing diameter
  body = FakeBody("Ceres", np.nan)

  # Testing search with no result
  search_result = {"Value": None}

  # Range expected
  expected_range = (2.809, 5.778)

  # Mock the search and the range to not depend on external tools
  with patch("src.diameter.find_diameter", return_value=search_result) as mock_find, patch("src.diameter.get_range", return_value=expected_range) as mock_range:
    handle_diameter(body, token="fake_token")

  # Verify that find_diameter was called only once
  mock_find.assert_called_once_with(
    ["Ceres"],
    amount=500,
    token="fake_token",
    verbose=False
  )

  # Verify that get_range was called only once
  mock_range.assert_called_once_with("Ceres")

  # The diameter must remain as nan
  assert np.isnan(body.diameter.value)