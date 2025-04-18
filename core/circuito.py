class Circuito:
    def __init__(self):
        self.componentes = []
        self.nodos = set()
        self.conexiones = {}
        
    def agregar_componente(self, componente):
        self.componentes.append(componente)
        self.nodos.add(componente.nodo1)
        if componente.nodo2 is not None:
            self.nodos.add(componente.nodo2)
        self.actualizar_conexiones(componente)
        
    def actualizar_conexiones(self, componente):
        if componente.nodo1 not in self.conexiones:
            self.conexiones[componente.nodo1] = []
        self.conexiones[componente.nodo1].append(componente)
        
        if componente.nodo2 is not None:
            if componente.nodo2 not in self.conexiones:
                self.conexiones[componente.nodo2] = []
            self.conexiones[componente.nodo2].append(componente)
            
    def verificar_conexiones(self):
        problemas = []
        
        for nodo, componentes in self.conexiones.items():
            if nodo is None:
                continue
                
            if isinstance(componentes[0], Tierra) and len(componentes) > 1:
                problemas.append(f"Demasiadas conexiones a tierra en nodo {nodo}")
                
            if len(componentes) < 2 and not any(isinstance(c, Tierra) for c in componentes):
                problemas.append(f"Nodo {nodo} puede estar flotando")
                
        return problemas
        
    def obtener_componentes_conectados(self, nodo):
        return self.conexiones.get(nodo, [])
        
    def obtener_matrices_nodales(self, frecuencia):
        num_nodos = len(self.nodos)
        if num_nodos < 2:
            return None, None
            
        nodo_indices = {nodo: i for i, nodo in enumerate(sorted(self.nodos))}
        
        Y = [[0j for _ in range(num_nodos)] for _ in range(num_nodos)]
        I = [0j for _ in range(num_nodos)]
        
        for componente in self.componentes:
            if isinstance(componente, Tierra):
                continue
                
            z = componente.impedancia(frecuencia)
            if z == float('inf'):
                continue
                
            n1 = nodo_indices[componente.nodo1]
            n2 = nodo_indices.get(componente.nodo2, -1)
            
            if z != 0:
                y = 1 / z
            else:
                y = 0
                
            if n2 != -1:
                Y[n1][n1] += y
                Y[n2][n2] += y
                Y[n1][n2] -= y
                Y[n2][n1] -= y
                
            if isinstance(componente, (FuenteDC, FuenteAC)):
                if n2 == -1:
                    I[n1] += componente.voltaje if isinstance(componente, FuenteDC) else componente.amplitud
                    
        Y_reduced = [row[1:] for row in Y[1:]]
        I_reduced = I[1:]
        
        return Y_reduced, I_reduced