from local_config import update_localdatabase, get_config

def main():
    
    # Option to update
    update = False
    
    # Updating process
    if update:
        update_localdatabase()
        
    # Get settings
    settings = get_config()

    

if __name__ == "__main__":
    main()