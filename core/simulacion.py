import numpy as np
from numpy.linalg import solve

def analizar_circuito(circuito, tiempo_simulacion=1.0, puntos=1000):
    resultados = {}
    t = np.linspace(0, tiempo_simulacion, puntos)
    
    # Análisis DC
    Y_dc, I_dc = circuito.obtener_matrices_nodales(0)
    if Y_dc and I_dc:
        try:
            V_dc = solve(Y_dc, I_dc)
            # Procesar resultados DC
        except:
            pass
    
    # Análisis AC
    has_ac = any(isinstance(c, FuenteAC) for c in circuito.componentes)
    if has_ac:
        frecuencias = {c.frecuencia for c in circuito.componentes if isinstance(c, FuenteAC)}
        for freq in frecuencias:
            Y_ac, I_ac = circuito.obtener_matrices_nodales(freq)
            if Y_ac and I_ac:
                try:
                    V_ac = solve(Y_ac, I_ac)
                    # Procesar resultados AC
                except:
                    pass
    
    # Simulación en el dominio del tiempo
    for componente in circuito.componentes:
        comp_data = {
            "voltaje": np.zeros_like(t),
            "corriente": np.zeros_like(t),
            "potencia": np.zeros_like(t),
            "tiempo": t
        }
        
        if isinstance(componente, FuenteAC):
            comp_data["voltaje"] = componente.voltaje_instantaneo(t)
            if hasattr(componente, 'impedancia_carga'):
                z = componente.impedancia_carga
                comp_data["corriente"] = comp_data["voltaje"] / z
            comp_data["potencia"] = comp_data["voltaje"] * comp_data["corriente"]
            
        elif isinstance(componente, Resistencia):
            comp_data["voltaje"] = np.sin(t * 2 * np.pi * 1)  # Ejemplo simplificado
            comp_data["corriente"] = comp_data["voltaje"] / componente.resistencia
            comp_data["potencia"] = comp_data["voltaje"] * comp_data["corriente"]
            
        elif isinstance(componente, (Capacitor, Inductor)):
            comp_data["voltaje"] = np.sin(t * 2 * np.pi * 1)
            comp_data["corriente"] = np.cos(t * 2 * np.pi * 1)
            comp_data["potencia"] = comp_data["voltaje"] * comp_data["corriente"]
            
        # Cálculos adicionales
        comp_data['potencia_promedio'] = np.mean(comp_data['potencia'])
        comp_data['vrms'] = np.sqrt(np.mean(comp_data['voltaje']**2))
        comp_data['irms'] = np.sqrt(np.mean(comp_data['corriente']**2))
        comp_data['potencia_aparente'] = comp_data['vrms'] * comp_data['irms']
        
        if isinstance(componente, (Resistencia, FuenteDC)):
            comp_data['factor_potencia'] = 1.0
        else:
            comp_data['factor_potencia'] = comp_data['potencia_promedio'] / comp_data['potencia_aparente'] if comp_data['potencia_aparente'] > 0 else 0
        
        resultados[componente] = comp_data
    
    return resultados