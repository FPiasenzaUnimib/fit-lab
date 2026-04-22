
import numpy as np

def modello(x, m, b):
    return m * x + b

def derivata_modello(x, m, b):
    return np.full_like(x, m)

configurazione = {
    "iniziali": {"m": 1.0, "b": 0.0},
#    "limiti": {"m": (None,None)},
#   "fissati": {"m": False}
}

descrizione = {
    "titolo": "Retta",
    "equazione": r"$y = \mu x + \beta$",
    "nomi": {
        "m": r"$\mu$", 
        "b": r"$\beta$",
        "asse_x": r"coordinata $x$",
        "asse_y": r"coordinata $y$"
    },
    "misure": {
        "m": "",
        "b": "",
        "asse_x": "",
        "asse_y": ""
    }
}
