from PySide6 import QtWidgets
from PySide6 import QtCore
import sys
import arwimporter.model

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    model = arwimporter.model.ARWIModel()
    view = QtWidgets.QTreeView()
    view.setModel(model)
    view.setWindowTitle('ARW Importer Tree Model Test')
    view.setIconSize( QtCore.QSize(32,32) )
#    view.setViewMode( QtWidgets.QListView.IconMode )
    view.setSelectionMode( QtWidgets.QAbstractItemView.ExtendedSelection )
    view.show()
    sys.exit( app.exec_() )
    
    
