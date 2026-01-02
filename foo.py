import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import  QPixmap
import pyexiv2
                                                     
if __name__ == "__main__":
    app = QApplication(sys.argv)
    md = pyexiv2.ImageMetadata(sys.argv[1])
    md.read()
    preview = md.previews[1]
    pixmap = QPixmap()
    pixmap.loadFromData(preview.data)
    label = QLabel()
    label.setPixmap( pixmap )
    label.show()
    
    sys.exit(app.exec_())
