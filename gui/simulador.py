from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget, 
                           QTableWidget, QTableWidgetItem, QPushButton, 
                           QFileDialog, QLabel)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from utils.graficas import generar_graficas
from utils.fourier import analizar_fourier
from utils.exportar import exportar_csv, exportar_json, exportar_graficas
from core.simulacion import analizar_circuito
import numpy as np

class SimuladorDialog(QDialog):
    def __init__(self, circuito, parent=None):
        super().__init__(parent)
        self.circuito = circuito
        self.parent_window = parent
        self.setWindowTitle("Resultados de Simulación")
        self.setGeometry(200, 200, 1000, 800)
        
        self.resultados = None
        self.initUI()
        self.simular()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Etiqueta de información
        self.info_label = QLabel()
        layout.addWidget(self.info_label)
        
        # Pestañas
        self.tabs = QTabWidget()
        
        # Pestaña de gráficos
        self.tab_graficos = QWidget()
        self.layout_graficos = QVBoxLayout()
        
        self.figura = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.figura)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.layout_graficos.addWidget(self.toolbar)
        self.layout_graficos.addWidget(self.canvas)
        
        self.tab_graficos.setLayout(self.layout_graficos)
        self.tabs.addTab(self.tab_graficos, "Gráficos")
        
        # Pestaña de resultados
        self.tab_resultados = QWidget()
        self.layout_resultados = QVBoxLayout()
        
        self.tabla_resultados = QTableWidget()
        self.layout_resultados.addWidget(self.tabla_resultados)
        
        self.tab_resultados.setLayout(self.layout_resultados)
        self.tabs.addTab(self.tab_resultados, "Resultados")
        
        # Pestaña de Fourier
        self.tab_fourier = QWidget()
        self.layout_fourier = QVBoxLayout()
        
        self.figura_fourier = Figure(figsize=(10, 8), dpi=100)
        self.canvas_fourier = FigureCanvas(self.figura_fourier)
        self.toolbar_fourier = NavigationToolbar(self.canvas_fourier, self)
        
        self.layout_fourier.addWidget(self.toolbar_fourier)
        self.layout_fourier.addWidget(self.canvas_fourier)
        
        self.tab_fourier.setLayout(self.layout_fourier)
        self.tabs.addTab(self.tab_fourier, "Análisis Fourier")
        
        layout.addWidget(self.tabs)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        self.btn_exportar = QPushButton("Exportar Resultados")
        self.btn_exportar.clicked.connect(self.exportar_resultados)
        btn_layout.addWidget(self.btn_exportar)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        btn_layout.addWidget(btn_cerrar)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def simular(self):
        self.resultados = analizar_circuito(self.circuito)
        
        num_comp = len(self.resultados)
        has_ac = any(isinstance(c, FuenteAC) for c in self.resultados.keys())
        has_dc = any(isinstance(c, FuenteDC) for c in self.resultados.keys())
        
        info_text = f"Circuito analizado: {num_comp} componentes | "
        info_text += "AC" if has_ac else ""
        info_text += " y " if has_ac and has_dc else ""
        info_text += "DC" if has_dc else ""
        self.info_label.setText(info_text)
        
        self.mostrar_resultados(self.resultados)
        self.mostrar_graficas(self.resultados)
        
    def mostrar_resultados(self, resultados):
        self.tabla_resultados.setRowCount(len(resultados))
        self.tabla_resultados.setColumnCount(6)
        headers = ["Componente", "V RMS", "I RMS", "P Promedio", "P Aparente", "FP"]
        self.tabla_resultados.setHorizontalHeaderLabels(headers)
        
        for i, (comp, datos) in enumerate(resultados.items()):
            self.tabla_resultados.setItem(i, 0, QTableWidgetItem(str(comp)))
            self.tabla_resultados.setItem(i, 1, QTableWidgetItem(f"{datos['vrms']:.4f} V"))
            self.tabla_resultados.setItem(i, 2, QTableWidgetItem(f"{datos['irms']:.4f} A"))
            self.tabla_resultados.setItem(i, 3, QTableWidgetItem(f"{datos['potencia_promedio']:.4f} W"))
            self.tabla_resultados.setItem(i, 4, QTableWidgetItem(f"{datos['potencia_aparente']:.4f} VA"))
            self.tabla_resultados.setItem(i, 5, QTableWidgetItem(f"{datos['factor_potencia']:.4f}"))
            
        self.tabla_resultados.resizeColumnsToContents()
        
    def mostrar_graficas(self, resultados):
        self.figura.clear()
        generar_graficas(self.figura, resultados)
        self.canvas.draw()
        
        for componente, datos in resultados.items():
            if isinstance(componente, FuenteAC):
                analisis_fourier = analizar_fourier(datos["voltaje"], datos["tiempo"], componente.frecuencia)
                self.mostrar_fourier(analisis_fourier)
                break
                
    def mostrar_fourier(self, analisis):
        self.figura_fourier.clear()
        
        ax1 = self.figura_fourier.add_subplot(2, 1, 1)
        ax1.set_title("Espectro de Frecuencia")
        ax1.set_xlabel("Frecuencia (Hz)")
        ax1.set_ylabel("Amplitud (V)")
        ax1.stem(analisis['frecuencias'], analisis['amplitudes'], basefmt=" ")
        ax1.set_xlim(0, min(10*analisis['frecuencia_fundamental'], analisis['frecuencias'][-1]))
        ax1.grid(True)
        
        ax2 = self.figura_fourier.add_subplot(2, 1, 2)
        ax2.axis('off')
        
        info_text = f"Frecuencia Fundamental: {analisis['frecuencia_fundamental']:.2f} Hz\n"
        info_text += f"THD: {analisis['thd']*100:.2f}%\n\n"
        info_text += "Armónicos significativos (>1%):\n"
        
        if analisis['armonicos']:
            for freq, amp in analisis['armonicos']:
                rel_amp = (amp / analisis['amplitudes'][0]) * 100
                if rel_amp > 1:
                    info_text += f"• {freq:.2f} Hz: {amp:.4f} V ({rel_amp:.1f}%)\n"
        else:
            info_text += "No se detectaron armónicos significativos"
            
        ax2.text(0.05, 0.05, info_text, fontsize=10, va='bottom')
        
        self.figura_fourier.tight_layout()
        self.canvas_fourier.draw()
        
    def exportar_resultados(self):
        if not self.resultados:
            QMessageBox.warning(self, "Error", "No hay resultados para exportar")
            return
            
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exportar Resultados", "", 
            "CSV (*.csv);;JSON (*.json);;PNG (*.png);;Todos los archivos (*)", 
            options=options)
            
        if not filename:
            return
            
        try:
            if filename.endswith('.csv') or '.csv' in filename:
                if not filename.endswith('.csv'):
                    filename += '.csv'
                exportar_csv(self.resultados, filename)
            elif filename.endswith('.json') or '.json' in filename:
                if not filename.endswith('.json'):
                    filename += '.json'
                exportar_json(self.resultados, filename)
            elif filename.endswith('.png') or '.png' in filename:
                if not filename.endswith('.png'):
                    filename += '.png'
                figuras = [self.figura, self.figura_fourier]
                exportar_graficas(figuras, filename[:-4])
            else:
                QMessageBox.warning(self, "Error", "Formato de archivo no soportado")
                return
                
            self.parent_window.status_bar.showMessage(f"Resultados exportados a {filename}")
            QMessageBox.information(self, "Éxito", f"Resultados exportados correctamente a:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar los resultados:\n{str(e)}")