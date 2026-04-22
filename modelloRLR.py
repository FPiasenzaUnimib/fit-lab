import numpy as np

def modello(x, R, L):
    return (x * L)/np.sqrt(R**2 + (x * L)**2)

def derivata_modello(x, R, L):
    return np.full_like(x, 1)

configurazione = {
    "iniziali": {"R": 100, "L": 0.1},
    "limiti": {"R": (0, None), "L": (0, None)}
}

descrizione = {
    "titolo": "Funzione di trasferimento su L",
    "equazione": r"$\frac{R}{\sqrt{R^2+(\omega L )^2}}$",
    "nomi": {
        "R": r"$R$",
        "L": r"$L$",
        "asse_x": r"Pulsazione $\omega$",
        "asse_y": r"$H(\omega)"
    },
    "misure": {
        "R": "",
        "L": "",
        "asse_x": "",
        "asse_y": ""
    } 
}