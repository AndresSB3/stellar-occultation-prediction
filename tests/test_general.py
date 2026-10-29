
from unittest.mock import call, patch

from occultations.core.general import run


# Test run with multiple bodies
def test_run_multiple_ids():
  
  # Fake settings and body
  fake_settings = {
    "body": {"id": ["Ceres", "Phoebe", "Arrokoth"]},
    "epoch": "example_epoch",
    "database": "example_database",
    "ADS_key": "1234567890",
  }

  # Use mocks to not depend on external functions
  with patch("occultations.core.general.Body") as mock_body, patch("occultations.core.general.handle_diameter") as mock_diameter, patch("occultations.core.general.get_eph", return_value="fake_eph") as mock_eph, patch("occultations.core.general.EphemTable") as mock_table:
    run(fake_settings)

  # get_eph, body, diameter and EphemTable should be called three times in this case
  assert mock_body.call_count == 3
  assert mock_diameter.call_count == 3
  assert mock_eph.call_count == 3
  assert mock_table.call_count == 3

  # Also, body must have the specific ids from the fake settings
  mock_body.assert_has_calls([
    call("Ceres"), call("Phoebe"), call("Arrokoth"),
  ])

  # Same with eph
  mock_eph.assert_has_calls([
    call("Ceres", "example_epoch", "example_database", verbose=False),
    call("Phoebe", "example_epoch", "example_database", verbose=False),
    call("Arrokoth", "example_epoch", "example_database", verbose=False),
  ])

  # And diamter must have the key as well as the return from body
  mock_diameter.assert_has_calls([
    call(mock_body.return_value, "1234567890"),
    call(mock_body.return_value, "1234567890"),
    call(mock_body.return_value, "1234567890"),
  ])
