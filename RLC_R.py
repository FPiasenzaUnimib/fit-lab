import numpy as np

def modello(x, R, L, C):
    return R / (R + 1j*(x * L - 1/(x * C)))

def derivata_modello(x, R, L, C):
    #return (L * R**2)/np.power(R**2 + (x*L)**2, 1.5)
    return np.full_like(x,0)

#\sigma_H^2 = \sigma_|H|^2 + |H|^2\sigma_\theta^2
configurazione = {
    "iniziali": {"R": 675, "L": 0.01, "C": 0.0001},
    "limiti": {"R": (0, None), "L": (0, None), "C": (0, None)},
    "fissati": {"R": True, "L": False, "C": False}
}

descrizione = {
    "titolo": r"Funzione di trasferimento $H(\omega)$ su $R$",
    "equazione": r"$\frac{R}{R+i(\omega L - \frac{1}{\omega C})}$",
    "scala_x": "log",
    #"scala_y": "log", 
    "nomi": {
        "R": r"$R$",
        "L": r"$L$",
        "C": r"$C$",
        "asse_x": r"Pulsazione $\omega$",
        "asse_y": r"$H(\omega)$"
    },
    
    "misure": {
        "R": r"$\Omega$",
        "L": r"$H$",
        "C": r"$F$"
    } 
}