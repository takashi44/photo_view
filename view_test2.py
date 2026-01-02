from PySide6 import QtWidgets
from PySide6 import QtCore
import sys
import arwimporter.view

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = arwimporter.view.ARWIWindow()
    window.show()
    sys.exit( app.exec_() )
    
    
