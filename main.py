from occultations.core.defaulter import default
from occultations.core.general import run
from occultations.core.local_config import get_config, update_localdatabase


def main(verbose=False, update=False):
  
  # Updating process
  if update:
    update_localdatabase()
        
  # Get and default settings
  settings = get_config()
  settings = default(settings)
  
  # Run pipeline
  run(settings, verbose)
  

if __name__ == "__main__":
  main(verbose=True, update=False)