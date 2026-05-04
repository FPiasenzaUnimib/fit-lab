"""
fit.py 


"""
#il codice fa schifo di per se ma funziona

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

        sq2 = (np.real(self.y - fx)**2)/(np.real(self.errY)**2) + (np.imag(self.y - fx)**2)/(np.imag(self.errY)**2)
        #errore = np.abs(self.errY) ** 2 + np.abs((dfdx * self.errX)) ** 2
        #print(fx.shape)
        return np.sum(sq2)
        #return np.sum(np.abs(self.y - fx)** 2 / errore) 

#per non avere eX quando non serve
def fmts(x):
    fmt = ".3e" if abs(x) < 0.1 and x != 0 else ".3f"
    return f"{x:{fmt}}"

if __name__ == "__main__":
    #print(f"{len(sys.argv)}")

    paramExtra = 0 
    if '-nofit' in sys.argv:
        paramExtra += 1
        eseguiFit = False 
    else:
        eseguiFit = True
    
    if '-fase' in sys.argv:
        paramExtra += 1
        rappFase = True
    else: 
        rappFase = False

    if '-comp' in sys.argv:
        paramExtra += 1
        compForzato = True
    else:
        compForzato = False

    # se troppo pochi parametri allora quit
    if len(sys.argv) < 3 + paramExtra:
        nomeFileDati = input("\033[30mInserisci il nome del file dati: \033[0m")
        nomeModello = input("\033[30mInserisci il nome del modulo contente i dati del modello: \033[0m")
    else:
        nomeFileDati = sys.argv[1]
        nomeModello = sys.argv[2]

    try:
        if rappFase:
            datiX, ampiezza, fase, errX, errAmpiezza, errFase = np.loadtxt(nomeFileDati, dtype=np.float64).T
            datiY = ampiezza * np.exp(1j * fase, dtype=np.complex128)
            errY = np.sqrt((np.cos(fase)*errAmpiezza)**2 + (ampiezza * np.sin(fase) * errFase)**2) + 1j * np.sqrt((np.sin(fase * errAmpiezza))**2 + (ampiezza * np.cos(fase) * errFase)**2)
            del ampiezza, fase, errAmpiezza, errFase
        else:
            datiX, datiY, errX, errY = np.loadtxt(nomeFileDati, dtype=np.complex128).T
    
    except Exception as err:
        print(f"\033[31mIl caricamento del file dati è fallito:\n\tnumpy: {err}\033[0m")
        exit(1)


    #scarto rappresentazione complessa 
    #copio per liberare memoria inutile
    datiX = datiX.real.copy()
    errX = errX.real.copy()


    if rappFase or compForzato or datiY.imag.any():
        datiComplessi = True
        #copio in ogni caso per liberare la memoria dal file completo
        datiY = datiY.copy()
        errY = errY.copy()
        print("\033[36mI valori della funzione sono complessi\033[0m")
    else:
        datiComplessi = False
        print("\033[36mI valori della funzione sono reali\033[0m")
        datiY = datiY.real.copy()
        errY = errY.real.copy()


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
    if datiComplessi:
        ax.errorbar(datiX, datiY.real, errY.real, errX, fmt='o', ecolor="red", capsize=5.0, markerfacecolor='orange', markeredgecolor='red')
        ax.errorbar(datiX, datiY.imag, errY.imag, errX, fmt='o', ecolor="red", capsize=5.0, markerfacecolor='cyan', markeredgecolor='red')
    else:
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


    if eseguiFit:
        #imposto la cost function per il modello
        Q2modello = PropagatoreX(datiX, datiY, errX, errY, moduloModello.modello, moduloModello.derivata_modello)
        #lstqModello = LeastSquares(datiX, datiY, errY, moduloModello.modello)
        min = Minuit(Q2modello, **configModello["iniziali"], name=list(configModello["iniziali"].keys()))

        if not "limiti" in configModello:
            print("\033[33m'limiti' non presente nel dizionario di configurazione, nessun limite verrà impostato sui parametri\033[0m")

        if "fissati" in configModello:
            paramFissati = configModello["fissati"]
        else:
            paramFissati = {}

        #utilizzo la configurazione nel modello
        for par in configModello["iniziali"]:
            if "limiti" in configModello and par in configModello["limiti"]:
                min.limits[par] = configModello["limiti"][par]
            if par in paramFissati:
                min.fixed[par] = paramFissati[par]

        min.migrad()
        min.hesse()

        ndof = len(datiX) - min.nfit

        if 'equazione' in descModello:
            equazione = f"{descModello['equazione']}\n"
        else:
            print("\033[33m'equazione' non presente nel dizionario di descrizione, nessuna equazione verrà mostrata a schermo\033[0m")
            equazione = ""
        
        #formatting la label
        label = (equazione +
            '\n'.join(fr"{nomi[param]}: {fmts(min.values[param])} $\pm$ {fmts(min.errors[param])}{fr" {misure[param]}" if param in misure else ""}" for param in configModello["iniziali"] if not paramFissati.get(param, False)) +
            "\n" + fr"$\chi^2/$ndof: {fmts(min.fval / ndof)}" + "\n" + fr"p-value: {fmts(stats.chi2.sf(min.fval, ndof))}")

        xMin = np.min(datiX)
        xMax = np.max(datiX)

        #grafico del modello interpolato
        if not 'scala_x' in descModello or descModello['scala_x'] == 'linear':
            xAxis = np.linspace(xMin, xMax, 1000)
        elif descModello['scala_x'] == 'log':
            xAxis = np.logspace(np.log10(xMin), np.log10(xMax), 1000)
        #da aggiungere altri possibilmente


        yAxis = moduloModello.modello(xAxis, *min.values)

        if datiComplessi:
            ax.plot(
                xAxis, 
                yAxis.real, 
                label=label,
                color='blue'
            )
            ax.plot(
                xAxis, 
                yAxis.imag, 
                linestyle='--',
                color='blue'
            )
        else:
            #plot + label contenente risultati di fit
            ax.plot(
                xAxis, 
                yAxis, 
                label=label,
                color='blue'
            )

        ax.legend()

    plt.show()

    


