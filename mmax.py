import numpy as np


def modello(x, a, b, c):
    return a*x**2 + b*x + c


def derivata_modello(x, a, b, c):
    return 2*a*x + b
 

#\sigma_H^2 = \sigma_|H|^2 + |H|^2\sigma_\theta^2
configurazione = {
    "iniziali": {'a': 0, 'b': 0, 'c': 0},
    #"limiti": {"A": (None, None), "alpha0": (None, None)},
    #"fissati": {"A": False, "alpha0": False}
}

descrizione = {
    "titolo": r"Fit parabolico",
    #"scala_x": "log",
    #"scala_y": "symlog", 
    "nomi": {
    },
    
    "misure": {
    } 

}