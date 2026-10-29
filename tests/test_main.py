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
  with patch("main.get_config", return_value=fake_settings) as mock_config, patch("main.default", return_value=fake_settings) as mock_default, patch("main.update_localdatabase") as mock_update, patch("main.run") as mock_run:
    main()
    
  # Each mocked function must be called once
  mock_config.assert_called_once_with()
  mock_default.assert_called_once_with(fake_settings)
  mock_run.assert_called_once_with(fake_settings, False)
  
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
  with patch("main.get_config", return_value=fake_settings) as mock_config, patch("main.default", return_value=fake_settings) as mock_default, patch("main.update_localdatabase") as mock_update, patch("main.run") as mock_run:
    main(update=True)
    
  # Each mocked function must be called once
  mock_config.assert_called_once_with()
  mock_default.assert_called_once_with(fake_settings)
  mock_run.assert_called_once_with(fake_settings, False)
  
  # The update function must also be called once
  mock_update.assert_called_once_with()

def test_main_verbose():
  
  # Fake settings and body
  fake_settings = {
    'body': {'id': ['Ceres']},
    'epoch': 'example_epoch',
    'database': 'example_database',
    'ADS_key': '1234567890'
  }
  
  # Use mocks to not depend on external functions
  with patch("main.get_config", return_value=fake_settings) as mock_config, patch("main.default", return_value=fake_settings) as mock_default, patch("main.update_localdatabase") as mock_update, patch("main.run") as mock_run:
    main(verbose=True)
    
  # Each mocked function must be called once
  mock_config.assert_called_once_with()
  mock_default.assert_called_once_with(fake_settings)
  
  # Update must not be called
  mock_update.assert_not_called()
  
  # Run must be called once with verbose=True
  mock_run.assert_called_once_with(fake_settings, True)