"""Metadata access layer backed by python-exiv2 (PyPI package 'exiv2').

All EXIF/preview reading goes through this module so the rest of the app
does not depend on a specific metadata binding.
"""
import datetime

import exiv2

exiv2.LogMsg.setLevel( exiv2.LogMsg.Level.mute )
# first XMP parser init is not thread-safe; do it before any thread-pool reads
exiv2.XmpParser.initialize()

_DATETIME_KEYS = ('Exif.Photo.DateTimeOriginal', 'Exif.Image.DateTime')
_SEQUENCE_KEYS = ('Exif.Sony1.SequenceNumber', 'Exif.Sony2.SequenceNumber')
_DATETIME_FORMAT = '%Y:%m:%d %H:%M:%S'


def _openImage( path ):
    image = exiv2.ImageFactory.open( path )
    image.readMetadata()
    return image

def _findTag( exif_data, key ):
    pos = exif_data.findKey( exiv2.ExifKey(key) )
    if pos == exif_data.end():
        return None
    return pos


class ImageMetadata( object ):
    """Scalar metadata read eagerly so the exiv2 objects can be released."""

    def __init__( self, path ):
        self.path = path
        image = _openImage( path )
        exif = image.exifData()

        self.datetime = self._readDatetime( exif )
        self.orientation = self._readInt( exif, ('Exif.Image.Orientation',), 1 )
        self.sequence_number = self._readInt( exif, _SEQUENCE_KEYS, -1 )
        self.pixel_size = (image.pixelWidth(), image.pixelHeight())

    def _readDatetime( self, exif ):
        for key in _DATETIME_KEYS:
            tag = _findTag( exif, key )
            if tag:
                try:
                    return datetime.datetime.strptime( tag.toString(), _DATETIME_FORMAT )
                except ValueError:
                    continue
        return None

    def _readInt( self, exif, keys, default ):
        for key in keys:
            tag = _findTag( exif, key )
            if tag:
                return tag.toInt64()
        return default


def _previewImages( path ):
    image = _openImage( path )
    manager = exiv2.PreviewManager( image )
    # properties are ordered smallest to largest
    return manager, list( manager.getPreviewProperties() )

def thumbnailBytes( path ):
    """Smallest embedded preview (tree icon)."""
    manager, props = _previewImages( path )
    if not props:
        return None
    return bytes( manager.getPreviewImage( props[0] ).copy().data() )

def largestPreviewBytes( path ):
    """Largest embedded preview (RAW preview pane)."""
    manager, props = _previewImages( path )
    if not props:
        return None
    return bytes( manager.getPreviewImage( props[-1] ).copy().data() )

def largestPreviewSize( path ):
    manager, props = _previewImages( path )
    if not props:
        return (0, 0)
    return (props[-1].width_, props[-1].height_)
