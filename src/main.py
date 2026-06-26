from reader import get_config

def main():
    settings = get_config()
    print(settings['body']['id'])


if __name__ == "__main__":
    main()