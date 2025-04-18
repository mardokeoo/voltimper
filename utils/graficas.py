import numpy as np

def generar_graficas(fig, resultados):
    if not resultados:
        return
        
    t = next(iter(resultados.values()))["tiempo"]
    
    ax1 = fig.add_subplot(3, 1, 1)
    ax1.set_title("Voltajes en el tiempo")
    ax1.set_xlabel("Tiempo (s)")
    ax1.set_ylabel("Voltaje (V)")
    
    ax2 = fig.add_subplot(3, 1, 2)
    ax2.set_title("Corrientes en el tiempo")
    ax2.set_xlabel("Tiempo (s)")
    ax2.set_ylabel("Corriente (A)")
    
    ax3 = fig.add_subplot(3, 1, 3)
    ax3.set_title("Potencia en el tiempo")
    ax3.set_xlabel("Tiempo (s)")
    ax3.set_ylabel("Potencia (W)")
    
    for componente, datos in resultados.items():
        label = str(componente)
        ax1.plot(t, datos["voltaje"], label=label)
        ax2.plot(t, datos["corriente"], label=label)
        ax3.plot(t, datos["potencia"], label=label)
        
    ax1.legend()
    ax2.legend()
    ax3.legend()
    fig.tight_layout()