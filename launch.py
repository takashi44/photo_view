#!/usr/bin/env python

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
import sys
import photo_view.widget

import photo_view.logger
photo_view.logger.setDebug()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Photo View")
    QtGui.QGuiApplication.setApplicationDisplayName("Photo View")
    window = photo_view.widget.PV_MainWindow()
    window.show()
    sys.exit( app.exec_() )
    
    
