import sys
from PyQt5.QtWidgets import QApplication
from gui.editor import EditorCircuito

def main():
    app = QApplication(sys.argv)
    editor = EditorCircuito()
    editor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()