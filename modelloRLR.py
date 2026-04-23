import numpy as np

def modello(x, R, L):
    return (x * L)/np.sqrt(R**2 + (x * L)**2)

def derivata_modello(x, R, L):
    #return (L * R**2)/np.power(R**2 + (x*L)**2, 1.5)
    return np.full_like(x,0)

configurazione = {
    "iniziali": {"R": 600, "L": 0.1},
    "limiti": {"R": (0, None), "L": (0, None)}
}

descrizione = {
    "titolo": r"Funzione di trasferimento $|H(\omega)|$ su $L$",
    "equazione": r"$\frac{\omega L}{\sqrt{R^2+(\omega L )^2}}$",
    #"logaritmico_x": True,
    #"logaritmico_y": True, 
    "nomi": {
        "R": r"$R$",
        "L": r"$L$",
        "asse_x": r"Pulsazione $\omega$",
        "asse_y": r"$|H(\omega)|$"
    },
    "misure": {
        "R": "",
        "L": "",
        "asse_x": "",
        "asse_y": ""
    } 
}