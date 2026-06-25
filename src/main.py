from data.mpc import ephemerides

def main():
    print(ephemerides('ceres', step='1d', num=10, start='2020-01-01', obs='G37'))


if __name__ == "__main__":
    main()
