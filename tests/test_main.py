from unittest.mock import call, patch

from main import main


# Test update function in main with update=false
def test_main_update_false():
  
  # Fake settings and body
  fake_settings = {
    'body': {'id': ['Ceres']},
    'epoch': 'example_epoch',
    'database': 'example_database',
    'ADS_key': '1234567890'
  }
  
  # Use mocks to not depend on external functions
  with patch("main.get_config", return_value=fake_settings) as mock_config, patch("main.default", return_value=fake_settings) as mock_default, patch("main.Body") as mock_body, patch("main.handle_diameter") as mock_diameter, patch("main.update_localdatabase") as mock_update, patch("main.get_eph", return_value=("fake_eph", "fake_err")) as mock_eph:
    main()
    
  # Each mocked function must be called once
  mock_config.assert_called_once_with()
  mock_default.assert_called_once_with(fake_settings)
  mock_body.assert_called_once_with('Ceres')
  mock_diameter.assert_called_once_with(mock_body.return_value, fake_settings['ADS_key'])
  mock_eph.assert_called_once_with('Ceres', 'example_epoch', 'example_database', verbose=False)
  
  # The update function must not be called
  mock_update.assert_not_called()
  
# Test update function in main with update=True
def test_main_update_true():
  
  # Fake settings and body
  fake_settings = {
    'body': {'id': ['Ceres']},
    'epoch': 'example_epoch',
    'database': 'example_database',
    'ADS_key': '1234567890'
  }
  
  # Use mocks to not depend on external functions
  with patch("main.get_config", return_value=fake_settings) as mock_config, patch("main.default", return_value=fake_settings) as mock_default, patch("main.Body") as mock_body, patch("main.handle_diameter") as mock_diameter, patch("main.update_localdatabase") as mock_update, patch("main.get_eph", return_value=("fake_eph", "fake_err")) as mock_eph:
    main(update=True)
    
  # Each mocked function must be called once
  mock_config.assert_called_once_with()
  mock_default.assert_called_once_with(fake_settings)
  mock_body.assert_called_once_with('Ceres')
  mock_diameter.assert_called_once_with(mock_body.return_value, fake_settings['ADS_key'])
  mock_eph.assert_called_once_with('Ceres', 'example_epoch', 'example_database', verbose=False)
  
  # The update function must also be called once
  mock_update.assert_called_once_with()
  
# Test main with multiple bodies
def test_main_multiple_ids():
  
  # Fake settings and body
  fake_settings = {
    'body': {'id': ['Ceres', 'Phoebe', 'Arrokoth']},
    'epoch': 'example_epoch',
    'database': 'example_database',
    'ADS_key': '1234567890'
  }
  
  # Use mocks to not depend on external functions
  with patch("main.get_config", return_value=fake_settings) as mock_config, patch("main.default", return_value=fake_settings) as mock_default, patch("main.Body") as mock_body, patch("main.handle_diameter") as mock_diameter, patch("main.update_localdatabase") as mock_update, patch("main.get_eph", return_value=("fake_eph", "fake_err")) as mock_eph:
    main(update=True)
    
  # Update, config, and default should be called only once
  mock_update.assert_called_once_with()
  mock_config.assert_called_once_with()
  mock_default.assert_called_once_with(fake_settings)
  
  # get_eph, body and diameter should be called three times in this case
  assert mock_eph.call_count == 3
  assert mock_body.call_count == 3
  assert mock_diameter.call_count == 3
  
  # Also, body must have the specific ids from the fake settings
  mock_body.assert_has_calls([
    call('Ceres'), call('Phoebe'), call('Arrokoth')
  ])
  
  # Same with eph
  mock_eph.assert_has_calls([
    call('Ceres', 'example_epoch', 'example_database', verbose=False),
    call('Phoebe', 'example_epoch', 'example_database', verbose=False),
    call('Arrokoth', 'example_epoch', 'example_database', verbose=False)
  ])