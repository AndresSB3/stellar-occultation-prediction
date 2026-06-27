from reader import get_config, default

def main():
    settings = get_config()
    settings = default(settings)


if __name__ == "__main__":
    main()