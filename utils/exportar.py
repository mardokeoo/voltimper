import csv
import json
import numpy as np
from datetime import datetime

def exportar_csv(resultados, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        headers = ['Tiempo (s)']
        for componente in resultados.keys():
            headers.extend([f"{componente} V (V)", f"{componente} I (A)", f"{componente} P (W)"])
        writer.writerow(headers)
        
        tiempo = next(iter(resultados.values()))['tiempo']
        for i, t in enumerate(tiempo):
            row = [t]
            for datos in resultados.values():
                row.extend([datos['voltaje'][i], datos['corriente'][i], datos['potencia'][i]])
            writer.writerow(row)

def exportar_json(resultados, filename):
    export_data = {
        'metadata': {
            'fecha': datetime.now().isoformat(),
            'componentes': [str(comp) for comp in resultados.keys()]
        },
        'data': {}
    }
    
    tiempo = next(iter(resultados.values()))['tiempo']
    export_data['data']['tiempo'] = tiempo.tolist()
    
    for componente, datos in resultados.items():
        export_data['data'][str(componente)] = {
            'voltaje': datos['voltaje'].tolist(),
            'corriente': datos['corriente'].tolist(),
            'potencia': datos['potencia'].tolist(),
            'vrms': datos['vrms'],
            'irms': datos['irms'],
            'potencia_promedio': datos['potencia_promedio'],
            'potencia_aparente': datos['potencia_aparente'],
            'factor_potencia': datos['factor_potencia']
        }
    
    with open(filename, 'w') as jsonfile:
        json.dump(export_data, jsonfile, indent=4)

def exportar_graficas(figuras, filename_prefix):
    for i, fig in enumerate(figuras):
        fig.savefig(f"{filename_prefix}_{i}.png", dpi=300, bbox_inches='tight')