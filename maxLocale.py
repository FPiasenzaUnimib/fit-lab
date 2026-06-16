import numpy as np
import matplotlib.pyplot as plt
import sys
import fit
from fmts import fmts

if __name__ == "__main__":
    #print(f"{len(sys.argv)}")

    

    # se troppo pochi parametri allora quit
    if len(sys.argv) < 2:
        nomeFileDati = input("\033[30mInserisci il nome del file dati: \033[0m")
    else:
        nomeFileDati = sys.argv[1]

    try:
        fitResult = fit.fit(nomeFileDati, 'mmax', eseguiFit=True, rappFase=False, compForzato=False)
        if fitResult == None:
            raise Exception("\033[31mNessun risultato fit utilizzabile\033[0m")
        if fitResult.covariance == None:
            raise Exception("\033[31mNessun errore utilizzabile\033[0m")
        a, b = fitResult.values['a'], fitResult.values['b']
        xMax = -b/2/a
        sxMax = np.sqrt(b**2/(4*a**4)*fitResult.covariance['a','a'] + 1/(4*a**2)*fitResult.covariance['b','b']-b/(2*a**3)*fitResult.covariance['a','b'])
        print(f"massimo in {fmts(xMax)} ± {fmts(sxMax)}")


    except Exception as err:
        print(err, file=sys.stderr)
        exit(1)