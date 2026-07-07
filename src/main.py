from local_config import update_localdatabase, get_config
from defaulter import default

def main():
    
  # Option to update
  update = False
  
  # Updating process
  if update:
    update_localdatabase()
        
  # Get settings
  settings = get_config()
    
  # Default settings
  settings = default(settings)
  print(settings)
    

if __name__ == "__main__":
  main()