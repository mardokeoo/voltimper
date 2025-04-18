import numpy as np
from abc import ABC, abstractmethod

class Componente(ABC):
    def __init__(self, nombre, nodo1, nodo2):
        self.nombre = nombre
        self.nodo1 = nodo1
        self.nodo2 = nodo2
        
    @abstractmethod
    def impedancia(self, frecuencia):
        pass
        
    @abstractmethod
    def __str__(self):
        pass

class Resistencia(Componente):
    def __init__(self, nombre, nodo1, nodo2, resistencia):
        super().__init__(nombre, nodo1, nodo2)
        self.resistencia = resistencia
        
    def impedancia(self, frecuencia):
        return self.resistencia
        
    def __str__(self):
        return f"R{self.nombre} ({self.resistencia} Ω)"

class Capacitor(Componente):
    def __init__(self, nombre, nodo1, nodo2, capacitancia):
        super().__init__(nombre, nodo1, nodo2)
        self.capacitancia = capacitancia
        
    def impedancia(self, frecuencia):
        if frecuencia == 0:
            return float('inf')
        return 1 / (2j * np.pi * frecuencia * self.capacitancia)
        
    def __str__(self):
        return f"C{self.nombre} ({self.capacitancia} F)"

class Inductor(Componente):
    def __init__(self, nombre, nodo1, nodo2, inductancia):
        super().__init__(nombre, nodo1, nodo2)
        self.inductancia = inductancia
        
    def impedancia(self, frecuencia):
        if frecuencia == 0:
            return 0
        return 2j * np.pi * frecuencia * self.inductancia
        
    def __str__(self):
        return f"L{self.nombre} ({self.inductancia} H)"

class FuenteDC(Componente):
    def __init__(self, nombre, nodo1, nodo2, voltaje):
        super().__init__(nombre, nodo1, nodo2)
        self.voltaje = voltaje
        
    def impedancia(self, frecuencia):
        return 0
        
    def __str__(self):
        return f"V{self.nombre} DC ({self.voltaje} V)"

class FuenteAC(Componente):
    def __init__(self, nombre, nodo1, nodo2, amplitud, frecuencia, fase=0):
        super().__init__(nombre, nodo1, nodo2)
        self.amplitud = amplitud
        self.frecuencia = frecuencia
        self.fase = fase
        
    def voltaje_instantaneo(self, t):
        return self.amplitud * np.sin(2 * np.pi * self.frecuencia * t + np.deg2rad(self.fase))
        
    def impedancia(self, frecuencia):
        return 0
        
    def __str__(self):
        return f"V{self.nombre} AC ({self.amplitud} V, {self.frecuencia} Hz)"

class Tierra(Componente):
    def __init__(self, nombre, nodo):
        super().__init__(nombre, nodo, None)
        
    def impedancia(self, frecuencia):
        return 0
        
    def __str__(self):
        return f"GND{self.nombre}"

class Cable(Componente):
    def __init__(self, nombre, nodo1, nodo2):
        super().__init__(nombre, nodo1, nodo2)
        
    def impedancia(self, frecuencia):
        return 0
        
    def __str__(self):
        return f"Wire{self.nombre}"

class Diodo(Componente):
    def __init__(self, nombre, nodo1, nodo2, Is=1e-12, Vt=0.02585, n=1):
        super().__init__(nombre, nodo1, nodo2)
        self.Is = Is
        self.Vt = Vt
        self.n = n
        
    def impedancia(self, frecuencia, voltaje=0):
        if voltaje == 0:
            return float('inf')
        rd = self.n * self.Vt / (self.Is * np.exp(voltaje / (self.n * self.Vt)))
        return rd
        
    def corriente(self, voltaje):
        return self.Is * (np.exp(voltaje / (self.n * self.Vt)) - 1)
        
    def __str__(self):
        return f"D{self.nombre}"

class TransistorBJT(Componente):
    def __init__(self, nombre, nodoB, nodoC, nodoE, beta=100, Vbe_on=0.7):
        super().__init__(nombre, None, None)
        self.nodoB = nodoB
        self.nodoC = nodoC
        self.nodoE = nodoE
        self.beta = beta
        self.Vbe_on = Vbe_on
        
    def impedancia(self, frecuencia, Vbe=0, Vce=0):
        if Vbe < self.Vbe_on:
            return (float('inf'), float('inf'), 0)
        gm = self.beta / (25e-3)
        return (float('inf'), 1/gm, 0)
        
    def __str__(self):
        return f"Q{self.nombre} (BJT)"