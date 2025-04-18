from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar, 
                           QAction, QGraphicsView, QGraphicsScene, QLabel, QStatusBar,
                           QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from core.componentes import (Resistencia, FuenteDC, FuenteAC, Capacitor, Inductor, 
                           Tierra, Cable, Diodo, TransistorBJT)
from core.circuito import Circuito
from gui.simulador import SimuladorDialog
import json
import os

class EditorCircuito(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoltImper - Editor de Circuitos")
        self.setGeometry(100, 100, 1000, 800)
        
        self.circuito = Circuito()
        self.current_file = None
        self.initUI()
        
    def initUI(self):
        # Barra de herramientas
        toolbar = QToolBar("Componentes")
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)
        
        # Componentes disponibles
        componentes = [
            ("Resistencia", "resistor.png", Resistencia),
            ("Fuente DC", "dc_source.png", FuenteDC),
            ("Fuente AC", "ac_source.png", FuenteAC),
            ("Capacitor", "capacitor.png", Capacitor),
            ("Inductor", "inductor.png", Inductor),
            ("Diodo", "diode.png", Diodo),
            ("Transistor BJT", "transistor.png", TransistorBJT),
            ("Tierra", "ground.png", Tierra),
            ("Cable", "wire.png", Cable)
        ]
        
        self.componentes_actions = []
        for nombre, icono, componente in componentes:
            icon_path = f"assets/{icono}" if os.path.exists(f"assets/{icono}") else ":/icons/component"
            action = QAction(QIcon(icon_path), nombre, self)
            action.setData(componente)
            action.triggered.connect(self.seleccionar_componente)
            toolbar.addAction(action)
            self.componentes_actions.append(action)
            
        # Área de dibujo
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.view.setSceneRect(0, 0, 800, 600)
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")
        
        # Menú
        self.init_menu()
        
        # Widget central
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Variables para la edición
        self.selected_component = None
        self.drawing_wire = False
        self.wire_start = None
        
    def init_menu(self):
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("Archivo")
        file_menu.addAction("Nuevo", self.nuevo_circuito, "Ctrl+N")
        file_menu.addAction("Abrir...", self.abrir_circuito, "Ctrl+O")
        file_menu.addAction("Guardar", self.guardar_circuito, "Ctrl+S")
        file_menu.addAction("Guardar como...", self.guardar_como_circuito)
        file_menu.addSeparator()
        file_menu.addAction("Salir", self.close)
        
        # Menú Edición
        edit_menu = menubar.addMenu("Edición")
        edit_menu.addAction("Deshacer", self.deshacer_accion, "Ctrl+Z")
        edit_menu.addAction("Rehacer", self.rehacer_accion, "Ctrl+Y")
        edit_menu.addSeparator()
        edit_menu.addAction("Eliminar", self.eliminar_seleccionado, "Del")
        
        # Menú Simulación
        sim_menu = menubar.addMenu("Simulación")
        sim_menu.addAction("Ejecutar Simulación", self.ejecutar_simulacion, "F5")
        sim_menu.addAction("Verificar Conexiones", self.verificar_conexiones)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("Ayuda")
        help_menu.addAction("Acerca de", self.mostrar_acerca_de)
        
    def seleccionar_componente(self):
        sender = self.sender()
        componente = sender.data()
        self.selected_component = componente
        self.status_bar.showMessage(f"Componente seleccionado: {componente.__name__} - Haz clic en el área de dibujo para colocarlo")
        
    def nuevo_circuito(self):
        if self.circuito.componentes:
            reply = QMessageBox.question(self, 'Nuevo circuito', 
                                       '¿Desea guardar el circuito actual antes de crear uno nuevo?',
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            
            if reply == QMessageBox.Yes:
                self.guardar_circuito()
            elif reply == QMessageBox.Cancel:
                return
                
        self.scene.clear()
        self.circuito = Circuito()
        self.current_file = None
        self.status_bar.showMessage("Nuevo circuito creado")
        
    def abrir_circuito(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Abrir Circuito", "", 
                                               "Circuit Files (*.cir);;All Files (*)", 
                                               options=options)
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    
                self.nuevo_circuito()
                self.current_file = filename
                self.status_bar.showMessage(f"Circuito cargado desde {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{str(e)}")
                
    def guardar_circuito(self):
        if self.current_file is None:
            self.guardar_como_circuito()
        else:
            self._guardar_a_archivo(self.current_file)
            
    def guardar_como_circuito(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar Circuito", "", 
                                                "Circuit Files (*.cir);;All Files (*)", 
                                                options=options)
        if filename:
            if not filename.endswith('.cir'):
                filename += '.cir'
            self._guardar_a_archivo(filename)
            self.current_file = filename
            
    def _guardar_a_archivo(self, filename):
        try:
            save_data = {
                'componentes': [],
                'conexiones': {}
            }
            
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=4)
                
            self.status_bar.showMessage(f"Circuito guardado en {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{str(e)}")
            
    def ejecutar_simulacion(self):
        if not self.circuito.componentes:
            self.status_bar.showMessage("Error: No hay componentes en el circuito")
            QMessageBox.warning(self, "Error", "El circuito no contiene componentes para simular")
            return
            
        problemas = self.circuito.verificar_conexiones()
        if problemas:
            msg = "\n".join(problemas)
            reply = QMessageBox.question(self, 'Problemas de conexión', 
                                       f"Se detectaron posibles problemas:\n{msg}\n\n¿Desea continuar con la simulación?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
                
        simulador = SimuladorDialog(self.circuito, self)
        simulador.exec_()
        
    def verificar_conexiones(self):
        problemas = self.circuito.verificar_conexiones()
        if problemas:
            msg = "\n".join(problemas)
            QMessageBox.warning(self, "Problemas de conexión", msg)
        else:
            QMessageBox.information(self, "Conexiones", "Todas las conexiones parecen correctas")
            
    def deshacer_accion(self):
        # Implementar lógica para deshacer
        pass
        
    def rehacer_accion(self):
        # Implementar lógica para rehacer
        pass
        
    def eliminar_seleccionado(self):
        # Implementar lógica para eliminar componente seleccionado
        pass
        
    def mostrar_acerca_de(self):
        about_text = """
        <h2>VoltImper - Simulador de Circuitos</h2>
        <p>Versión 1.0</p>
        <p>Un simulador de circuitos eléctricos para análisis AC/DC</p>
        <p>Características:</p>
        <ul>
            <li>Diseño de circuitos con interfaz gráfica</li>
            <li>Análisis en tiempo y frecuencia</li>
            <li>Componentes: R, L, C, fuentes, diodos, transistores</li>
            <li>Análisis de Fourier y THD</li>
            <li>Cálculo de potencia</li>
        </ul>
        <p>© 2023 - Desarrollado para fines educativos</p>
        """
        QMessageBox.about(self, "Acerca de VoltImper", about_text)