from unittest.mock import call, patch

from main import main


# Test update function in main with update=false
def test_main_update_false():
  
  # Fake settings and body
  fake_settings = {
    'body': {'id': ['Ceres']},
    'epoch': 'example_epoch',
    'ADS_key': '1234567890'
  }
  
  # Use mocks to not depend on external functions
  with patch("main.get_config", return_value=fake_settings) as mock_config, patch("main.default", return_value=fake_settings) as mock_default, patch("main.Body") as mock_body, patch("main.handle_diameter") as mock_diameter, patch("main.update_localdatabase") as mock_update:
    main()
    
  # Each mocked function must be called once
  mock_config.assert_called_once_with()
  mock_default.assert_called_once_with(fake_settings)
  mock_body.assert_called_once_with('Ceres')
  mock_diameter.assert_called_once_with(mock_body.return_value, fake_settings['ADS_key'])
  
  # The update function must not be called
  mock_update.assert_not_called()
  
# Test update function in main with update=True
def test_main_update_true():
  
  # Fake settings and body
  fake_settings = {
    'body': {'id': ['Ceres']},
    'epoch': 'example_epoch',
    'ADS_key': '1234567890'
  }
  
  # Use mocks to not depend on external functions
  with patch("main.get_config", return_value=fake_settings) as mock_config, patch("main.default", return_value=fake_settings) as mock_default, patch("main.Body") as mock_body, patch("main.handle_diameter") as mock_diameter, patch("main.update_localdatabase") as mock_update:
    main(update=True)
    
  # Each mocked function must be called once
  mock_config.assert_called_once_with()
  mock_default.assert_called_once_with(fake_settings)
  mock_body.assert_called_once_with('Ceres')
  mock_diameter.assert_called_once_with(mock_body.return_value, fake_settings['ADS_key'])
  
  # The update function must also be called once
  mock_update.assert_called_once_with()
  
# Test main with multiple bodies
def test_main_multiple_ids():
  
  # Fake settings and body
  fake_settings = {
    'body': {'id': ['Ceres', 'Phoebe', 'Arrokoth']},
    'epoch': 'example_epoch',
    'ADS_key': '1234567890'
  }
  
  # Use mocks to not depend on external functions
  with patch("main.get_config", return_value=fake_settings) as mock_config, patch("main.default", return_value=fake_settings) as mock_default, patch("main.Body") as mock_body, patch("main.handle_diameter") as mock_diameter, patch("main.update_localdatabase") as mock_update:
    main(update=True)
    
  # Update, config and default should be called only once
  mock_update.assert_called_once_with()
  mock_config.assert_called_once_with()
  mock_default.assert_called_once_with(fake_settings)
  
  # Body and diameter should be called three times in this case
  assert mock_body.call_count == 3
  assert mock_diameter.call_count == 3
  
  # Also, body must have the specific ids from the fake settings
  mock_body.assert_has_calls([
    call('Ceres'), call('Phoebe'), call('Arrokoth')
  ])