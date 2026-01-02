import sys
import exiv2
                                                     
if __name__ == "__main__":
    img = exiv2.ImageFactory.open(sys.argv[1])
    img.readMetadata()
    exif = img.exifData()
    thumb = exiv2.ExifThumb(exif)
    data = thumb.copy()

    pixmap = QPixmap()
    pixmap.loadFromData(bytes(data))
    label = QLabel()
    label.setPixmap( pixmap )
    label.show()
    
    sys.exit(app.exec_())
