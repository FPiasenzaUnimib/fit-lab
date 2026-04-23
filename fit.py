"""
fit.py 


"""

import numpy as np
import matplotlib.pyplot as plt
from iminuit import Minuit
import importlib
#from iminuit.cost import LeastSquares
from scipy import stats

import sys

# Equivalente di LeastSquares ma con propagazione su errore in X
class PropagatoreX:
    def __init__(self, x, y, errX, errY, modello, derivata_modello):
        self.x = x
        self.y = y
        self.errX = errX
        self.errY = errY
        self.modello = modello
        self.derivata = derivata_modello
    
    def __call__(self, *params):
        fx = self.modello(self.x, *params)
        dfdx = self.derivata(self.x, *params)

        errore = self.errY ** 2 + (dfdx * self.errX) ** 2
        #print(fx.shape)
        return np.sum((self.y - fx)** 2 / errore) 

#per non avere eX quando non serve
def fmts(x):
    fmt = ".3e" if abs(x) < 0.1 and x != 0 else ".3f"
    return f"{x:{fmt}}"

if __name__ == "__main__":
    #print(f"{len(sys.argv)}")

    # se troppo pochi parametri allora quit
    if len(sys.argv) < 3:
        nomeFileDati = input("\033[30mInserisci il nome del file dati: \033[0m")
        nomeModello = input("\033[30mInserisci il nome del modulo contente i dati del modello: \033[0m")
    else:
        nomeFileDati = sys.argv[1]
        nomeModello = sys.argv[2]
    
    try:
        datiX, datiY, errX, errY = np.loadtxt(nomeFileDati).T#, dtype=np.complex128).T
    except Exception as err:
        print(f"\033[31mIl caricamento del file dati è fallito:\n\tnumpy: {err}\033[0m")
        exit(1)
    #importazione del modulo contenente il modello e i dati relativi al modello
    #moduloModello = None
    try:
        moduloModello = importlib.import_module(nomeModello)

        if not hasattr(moduloModello, "modello"):
            raise ImportError("Il modulo non contiene il modello")
        if not hasattr(moduloModello, "derivata_modello"):
            raise ImportError("Il modulo non contiene la derivata del modello, necessaria per il calcolo dell'errore")
        if not hasattr(moduloModello, "configurazione"):
            raise ImportError("Il modulo non contiene un dizionario di configurazione")
        if not hasattr(moduloModello, "descrizione"):
            raise ImportError("Il modulo non contiene un dizionario di descrizione")
        
    except ImportError as err:
        print(f"\033[31mL'importazione del modulo contentente il modello è fallita: \n\t{err}\033[0m", file=sys.stderr)
        exit(1)
    #per facilita di utilizzo
    configModello = moduloModello.configurazione
    descModello = moduloModello.descrizione

    fig, ax = plt.subplots(1,1)

    if not 'iniziali' in configModello:
        print("\033[31m'iniziali' non presente nel dizionario di configurazione\033[0m", file=sys.stderr)
        exit(1)

    if 'nomi' in descModello:
        nomi = descModello['nomi']
    else:
        print("\033[33m'nomi' non presente nel dizionario di descrizione, utilizzo nomi di default\033[0m")
        nomi = { n: n for n in configModello['iniziali']}

    if 'misure' in descModello:
        misure = descModello['misure']
    else: 
        print("\033[33m'misure' non presente nel dizionario di descrizione, nessuna unità di misura verrà mostrata\033[0m")
        misure = {}

    if 'scala_x' in descModello:
        ax.set_xscale(descModello['scala_x'])
    if 'scala_y' in descModello:
        ax.set_yscale(descModello['scala_y'])

    #scatter plot iniziale dei dati
    ax.errorbar(datiX, datiY, errY, errX, fmt='o', ecolor="red", capsize=5.0, markerfacecolor='black', markeredgecolor='red')
   

    #imposto titolo e label
    if 'titolo' in descModello:
        ax.set_title(descModello['titolo'])
    else:
        print("\033[33m'titolo' non presente nel dizionario di descrizione, nessun titolo verrà mostrato a schermo\033[0m")
    
    if 'asse_x' in nomi:
        ax.set_xlabel(nomi['asse_x'] + (fr" ({misure['asse_x']})" if 'asse_x' in misure else ""))
    else:
        print("\033[33m'asse_x' non presente nel dizionario 'nomi', utilizzo label asse x default\033[0m")
        ax.set_xlabel("x" + (fr" ({misure['asse_x']})" if 'asse_x' in misure else ""))

    if 'asse_y' in nomi:
        ax.set_ylabel(nomi['asse_y'] + (fr" ({misure['asse_y']})" if 'asse_y' in misure else ""))
    else:
        print("\033[33m'asse_y' non presente nel dizionario 'nomi', utilizzo label asse y default\033[0m")
        ax.set_ylabel("y" + (fr" ({misure['asse_y']})" if 'asse_y' in misure else ""))


    #imposto la cost function per il modello
    Q2modello = PropagatoreX(datiX, datiY, errX, errY, moduloModello.modello, moduloModello.derivata_modello)
    #lstqModello = LeastSquares(datiX, datiY, errY, moduloModello.modello)
    min = Minuit(Q2modello, **configModello["iniziali"], name=list(configModello["iniziali"].keys()))

    if not "limiti" in configModello:
        print("\033[33m'limiti' non presente nel dizionario di configurazione, nessun limite verrà impostato sui parametri\033[0m")

    #utilizzo la configurazione nel modello
    for par in configModello["iniziali"]:
        if "limiti" in configModello and par in configModello["limiti"]:
            min.limits[par] = configModello["limiti"][par]
        if "fissati" in configModello and par in configModello["fissati"]:
            min.fixed[par] = configModello["fissati"][par]

    min.migrad()
    min.hesse()

    #grafico del modello interpolato
    xAxis = np.linspace(np.min(datiX), np.max(datiX), 1000)
    yAxis = moduloModello.modello(xAxis, *min.values)

    ndof = len(datiX) - min.nfit

    if 'equazione' in descModello:
        equazione = f"{descModello['equazione']}\n"
    else:
        print("\033[33m'equazione' non presente nel dizionario di descrizione, nessuna equazione verrà mostrata a schermo\033[0m")
        equazione = ""

    #plot + label contenente risultati di fit
    ax.plot(
        xAxis, 
        yAxis, 
        label= equazione +
            '\n'.join(fr"{nomi[param]}: {fmts(min.values[param])} $\pm$ {fmts(min.errors[param])} {misure[param] if param in misure else ""}" for param in configModello["iniziali"]) +
            "\n" + fr"$\chi^2/$ndof: {fmts(min.fval / ndof)}" + "\n" + fr"p-value: {fmts(stats.chi2.sf(min.fval, ndof))}",
        color='blue'
    )

    ax.legend()

    plt.show()

    


