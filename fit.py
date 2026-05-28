"""
fit.py 


"""
#il codice fa schifo di per se ma funziona

from typing import Callable, NoReturn
import numpy as np
import matplotlib.pyplot as plt
from iminuit import Minuit
import importlib
#from iminuit.cost import LeastSquares
from scipy import stats

import sys

# Equivalente di LeastSquares ma con propagazione su errore in X
class PropagatoreX:
    def __init__(self, x : np.ndarray, y : np.ndarray, errX : np.ndarray, errY : np.ndarray, modello : Callable, derivata_modello : Callable | None):
        self.x = x
        self.y = y
        self.errX = errX
        self.errY = errY
        self.modello = modello
        self.derivata = derivata_modello
    
    def __call__(self, *params) -> float:
        fx = self.modello(self.x, *params)
        dfdx = self.derivata(self.x, *params) if self.derivata != None else np.zeros_like(fx)

        diff = self.y - fx
        sq2 = (
            (diff.real**2)/(self.errY.real**2 + (dfdx.real*self.errX)**2) + (0 if not np.any(self.errY.imag) else (diff.imag**2)/(self.errY.imag**2 + (dfdx.imag * self.errX)**2)) 
        )
        #errore = np.abs(self.errY) ** 2 + np.abs((dfdx * self.errX)) ** 2
        #print(fx.shape)
        return np.sum(sq2)
        #return np.sum(np.abs(self.y - fx)** 2 / errore) 

#per non avere eX quando non serve
def fmts(x : float) -> str:
    fmt = ".3e" if abs(x) < 0.1 and x != 0 else ".3f"
    return f"{x:{fmt}}"

def fit(nomeFileDati : str, nomeModello : str, *, eseguiFit: bool = True, rappFase: bool = False, compForzato: bool = False) -> None | NoReturn:
    try:
        if rappFase:
            datiX, ampiezza, fase, errX, errAmpiezza, errFase = np.loadtxt(nomeFileDati, dtype=np.float64).T
            datiY = ampiezza * np.exp(1j * fase, dtype=np.complex128)
            errY = np.sqrt((np.cos(fase)*errAmpiezza)**2 + (ampiezza * np.sin(fase) * errFase)**2) + 1j * np.sqrt((np.sin(fase * errAmpiezza))**2 + (ampiezza * np.cos(fase) * errFase)**2)
            del ampiezza, fase, errAmpiezza, errFase
        else:
            datiX, datiY, errX, errY = np.loadtxt(nomeFileDati, dtype=np.complex128).T
    except Exception as err:
        raise Exception(f"\033[31mIl caricamento del file dati è fallito:\n\tnumpy: {err}\033[0m")
    #scarto rappresentazione complessa 
    #copio per liberare memoria inutile
    datiX = datiX.real.copy()
    errX = errX.real.copy()


    if rappFase or compForzato or datiY.imag.any():
        datiComplessi = True
        #copio in ogni caso per liberare la memoria dal file completo
        datiY = datiY.copy()
        errY = errY.copy()
        print("\033[36mI valori della funzione sono complessi\033[0m\n")
    else:
        datiComplessi = False
        print("\033[36mI valori della funzione sono reali\033[0m\n")
        datiY = datiY.real.copy()
        errY = errY.real.copy()


    #importazione del modulo contenente il modello e i dati relativi al modello
    #moduloModello = None
    try:
        moduloModello = importlib.import_module(nomeModello)

        if not hasattr(moduloModello, "modello"):
            raise Exception("Il modulo non contiene il modello")
        if not hasattr(moduloModello, "derivata_modello"):
            raise Exception("Il modulo non contiene la derivata del modello, necessaria per il calcolo dell'errore")
        if not hasattr(moduloModello, "configurazione"):
            raise Exception("Il modulo non contiene un dizionario di configurazione")
        if not hasattr(moduloModello, "descrizione"):
            raise Exception("Il modulo non contiene un dizionario di descrizione")
        
    except Exception as err:
        raise Exception(f"\033[31mL'importazione del modulo contentente il modello è fallita: \n\t{err}\033[0m")

    #per facilita di utilizzo
    configModello = moduloModello.configurazione
    descModello = moduloModello.descrizione

    fig, ax = plt.subplots(1,1)

    if not 'iniziali' in configModello:
        print("\033[31m'iniziali' non presente nel dizionario di configurazione\033[0m", file=sys.stderr)
        exit(1)

    if 'nomi' in descModello:
        nomi = { n: descModello['nomi'][n] if n in descModello['nomi'] else n for n in configModello['iniziali']}
        for n in configModello['iniziali']:
            if n not in descModello['nomi']:
                print(f"\033[33mParametro '{n}' non presente nel dizionario nomi, utilizzato format di default\033[0m")
        
        if 'asse_x' in descModello['nomi']:
            nomi.update({'asse_x' : descModello['nomi']['asse_x']})
        if 'asse_y' in descModello['nomi']:
            nomi.update({'asse_y' : descModello['nomi']['asse_y']})
    else:
        print("\033[33m'nomi' non presente nel dizionario di descrizione, utilizzo nomi di default\033[0m")
        nomi = { n: n for n in configModello['iniziali'] }

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


    if np.any(errY.real == 0) or (datiComplessi and np.any(errY.imag == 0)):
        print('\n\033[31mErrori nulli rilevati, nessun fit eseguito\033[0m')
        eseguiFit = False

    if eseguiFit:
        #imposto la cost function per il modello
        Q2modello = PropagatoreX(datiX, datiY, errX, errY, moduloModello.modello, moduloModello.derivata_modello)
        #lstqModello = LeastSquares(datiX, datiY, errY, moduloModello.modello)
        min = Minuit(Q2modello, **configModello["iniziali"], name=list(configModello["iniziali"].keys()))


        if "limiti" in configModello:
            limiti = configModello["limiti"]
        else:
            limiti = {}
            print("\033[33m'limiti' non presente nel dizionario di configurazione, nessun limite verrà impostato sui parametri\033[0m")

        if "fissati" in configModello:
            paramFissati = configModello["fissati"]
        else:
            paramFissati = {}

        #utilizzo la configurazione nel modello
        for par in configModello["iniziali"]:
            if par in limiti:
                min.limits[par] = limiti[par]
            if par in paramFissati:
                min.fixed[par] = paramFissati[par]

        min.migrad()
        min.hesse()

        #check di validita' fit con report (da fare)
        #errore dovuto a pylance
        if min.fmin.is_valid:
            print("\n\033[32mIl fit risulta valido\033[0m")
        else:
            print("\n\033[31mIl fit non risulta valido\033[0m")


        ndof = len(datiX) - min.nfit

        if 'equazione' in descModello:
            equazione = f"{descModello['equazione']}\n"
        else:
            print("\033[33m'equazione' non presente nel dizionario di descrizione, nessuna equazione verrà mostrata a schermo\033[0m")
            equazione = ""
        
        if min.fval != None:
            chi2_r = min.fval / ndof
            pvalue = stats.chi2.sf(min.fval, ndof)
        else: 
            chi2_r = pvalue = float('nan')

        print("\nValori:")
        print('\n'.join(f"{param} = {min.values[param]} ± {min.errors[param]}" for param in min.parameters))
        print("Covarianza: ")
        print(min.covariance)
        print(f"Chi2/ndof: {fmts(chi2_r)}, p-value: {fmts(pvalue)}\n")

        #formatting la label
        label = (equazione +
            '\n'.join(fr"{nomi[param]}: {fmts(min.values[param])} $\pm$ {fmts(min.errors[param])}{fr" {misure[param]}" if param in misure else ""}" for param in configModello["iniziali"] if not paramFissati.get(param, False)) +
            "\n" + fr"$\chi^2/$ndof: {fmts(chi2_r)}" + "\n" + fr"p-value: {fmts(pvalue)}")

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
                color='green'
            )

        ax.legend()

    plt.show()

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

    del paramExtra

    try:
        fit(nomeFileDati, nomeModello, eseguiFit=eseguiFit, rappFase=rappFase, compForzato=compForzato)
    except Exception as err:
        print(err, file=sys.stderr)
        exit(1)
    
    
    


    

    


