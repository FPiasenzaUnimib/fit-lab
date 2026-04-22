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

'''
fit.py filedati modelloDati 
'''
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
        return np.sum((self.y - fx)** 2 / errore) 

if __name__ == "__main__":
    #print(f"{len(sys.argv)}")


    # se troppo pochi parametri allora quit
    if len(sys.argv) < 3:
        nomeFileDati = input("Inserisci il nome del file dati: ")
        nomeModello = input("Inserisci il nome del modulo contente i dati del modello: ")
    else:
        nomeFileDati = sys.argv[1]
        nomeModello = sys.argv[2]
    datiX, datiY, errX, errY = np.loadtxt(nomeFileDati).T


    fig, ax = plt.subplots(1,1)

    #scatter plot iniziale dei dati
    ax.errorbar(datiX, datiY, errY, errX, fmt='o', ecolor="red", capsize=5.0, markerfacecolor='black', markeredgecolor='red')
   
    #importazione del modulo contenente il modello e i dati relativi al modello
    moduloModello = importlib.import_module(nomeModello)

    #per facilita di utilizzo
    configModello = moduloModello.configurazione
    descModello = moduloModello.descrizione

    #imposto titolo e label
    ax.set_title(descModello['titolo'])

    ax.set_xlabel(descModello['nomi']['asse_x'] + fr" {descModello['misure']['asse_x']}")
    ax.set_ylabel(descModello['nomi']['asse_y'] + fr" {descModello['misure']['asse_y']}")

    #imposto la cost function per il modello
    Q2modello = PropagatoreX(datiX, datiY, errX, errY, moduloModello.modello, moduloModello.derivata_modello)
    #lstqModello = LeastSquares(datiX, datiY, errY, moduloModello.modello)
    min = Minuit(Q2modello, **configModello["iniziali"], name=list(configModello["iniziali"].keys()))

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

    #plot + label contenente risultati di fit
    ax.plot(
        xAxis, 
        yAxis, 
        label=descModello['equazione']+ "\n" +
            '\n'.join(fr"{descModello['nomi'][param]}: {min.values[param]: .3f} $\pm$ {min.errors[param]: .3f} {descModello['misure'][param]}" for param in configModello["iniziali"]) +
            "\n" + fr"$\chi^2/$ndof: {min.fval / ndof: .3f}" + "\n" + fr"p-value: {stats.chi2.sf(min.fval, ndof): .3f}",
        color='blue'
    )

    ax.legend()

    plt.show()

    


