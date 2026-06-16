import numpy as np
import matplotlib.pyplot as plt
import sys


def main():
    try: 
        if len(sys.argv) < 2:
            raise Exception("\033[")
        datiX, datiY, errX, errY = np.loadtxt(nome_file)
    except Exception as e:
        pass

if __name__ == '__main__':
    main()