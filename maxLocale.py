import numpy as np
import matplotlib.pyplot as plt
import sys
import fit

if __name__ == "__main__":
    #print(f"{len(sys.argv)}")

    

    # se troppo pochi parametri allora quit
    if len(sys.argv) < 2:
        nomeFileDati = input("\033[30mInserisci il nome del file dati: \033[0m")
    else:
        nomeFileDati = sys.argv[1]

    try:
        fitResult = fit.fit(nomeFileDati, 'mmax', eseguiFit=True, rappFase=False, compForzato=False)

    except Exception as err:
        print(err, file=sys.stderr)
        exit(1)