import pyexiv2
import os
import re
import datetime
from . import config
from . import pathutil

class PV_BaseItem( object ):
    
    def __init__( self, data ):
        self._data = data
        self._children = []
        self._parent = None

    def removeChild( self, item ):
        if item in self._children:
            self._children.remove(item)
            return True
        return False

    def addChild( self, item ):
        self._checkItem( item )
        if item not in self._children:
            self._children.append( item )
        if item.parent and item.parent != self:
            item.parent.removeChild( item )
        item._parent = self
        self._children.sort( key=lambda a: a.datetime )

    def _checkItem( self, item ):
        pass

    @property
    def parent( self ):
        return self._parent

    @property
    def children( self ):
        return self._children

    @property
    def datetime( self ):
        raise NotImplementedError

    @property
    def name( self ):
        raise NotImplementedError

    @property
    def data( self ):
        return self._data

    @property
    def path( self ):
        return ''

    @property
    def thumbnail( self ):
        raise NotImplementedError

    @property
    def preview( self ):
        raise NotImplementedError

    @property
    def preview_size( self ):
        raise NotImplementedError

    @property
    def orientation( self ):
        return 0

    @property
    def sequence_number( self ):
        return -1


class PV_RootItem( PV_BaseItem ):
    IMG = pathutil.resolvePackagePath( config.data['folder_icon'] )
    
    def __init__( self, path ):
        super( PV_RootItem, self ).__init__( path )
        if not os.path.exists( path ):
            raise RuntimeError('Path does not exist: %s' % path )

    @property
    def name( self ):
        return self._data

    @property
    def thumbnail( self ):
        return self.IMG


class PV_DateGroupItem( PV_BaseItem ):
    IMG = pathutil.resolvePackagePath( config.data['continuous_shoot_icon'] )
    
    def __init__( self, data ):
        super( PV_DateGroupItem, self ).__init__( data )
        if not isinstance(self._data, datetime.datetime):
            self._data = datetime.datetime( *[int(a) for a in self._data.split('-')] )

    @property
    def name( self ):
        return self._data.date().isoformat()

    @property
    def datetime( self ):
        return self._data

    @property
    def path( self ):
        return self.name

    @property
    def thumbnail( self ):
        return self.IMG


class PV_ContinuousShootGroupItem( PV_BaseItem ):
    def __init__( self, data ):
        super( PV_ContinuousShootGroupItem, self ).__init__( data )
        if not isinstance(self._data, datetime.datetime):
            self._data = datetime.datetime( *[int(a) for a in self._data.split('-')] )

    @property
    def name( self ):
        if len(self._children):
            return '%s...(%d)' % (self._children[0].name, len(self.children))
        return ''
    
    @property
    def datetime( self ):
        return self._data

    @property
    def path( self ):
        if self.parent:
            return self.parent.path
        return ''


class PV_ImageItem( PV_BaseItem ):
    def __init__( self, path ):
        super( PV_ImageItem, self ).__init__( path )
        self.md = pyexiv2.ImageMetadata( path )
        self.md.read()

    def addChild( self, item ):
        raise RuntimeError('Unable to add child on ImageItem' )

    @property
    def datetime( self ):
        if 'Exif.Photo.DateTimeOriginal' in self.md:
            return self.md.get('Exif.Photo.DateTimeOriginal').value
        return self.md.get('Exif.Image.DateTime').value

    @property
    def name( self ):
        return os.path.basename( self._data )

    @property
    def thumbnail( self ):
        return self.md.previews[0].data

    @property
    def orientation( self ):
        return self.md.get('Exif.Image.Orientation').value

    @property
    def path( self ):
        path = self.name
        if self.parent:
            path = self.parent.path + '/' + self.name
        return path



class PV_JPG( PV_ImageItem ):

    @property
    def preview( self ):
        return self.md.buffer

    @property
    def preview_size( self ):
        return self.md.dimensions

    @property
    def sequence_number( self ):
        tag = self.md.get('Exif.Sony1.SequenceNumber')
        if tag:
            return tag.value
        return -1

class PV_ARW( PV_ImageItem ):

    @property
    def preview( self ):
        return self.md.previews[1].data

    @property
    def preview_size( self ):
        return self.md.previews[1].dimensions

    @property
    def sequence_number( self ):
        tag = self.md.get('Exif.Sony2.SequenceNumber')
        if tag:
            return tag.value
        return -1

class PV_MovieItem( PV_BaseItem ):
    def __init__( self, path ):
        super( PV_MovieItem, self ).__init__( path )



#===================================================
IMAGE_MAPPING = {'.jpg' : PV_JPG,
                 '.arw' : PV_ARW }
#===================================================

def findImages( root_dir=None ):
    if root_dir:
        root_dirs=[root_dir]
    else:
        root_dirs = config.data['image_root_dirs']

    extensions = config.data['image_extensions']
    extensions_pattern = '(' + '|'.join(extensions) + ')$'
    images = []
    for root_dir in root_dirs:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if re.search( extensions_pattern, file ):
                    path = os.path.join(root, file)
                    images.append( path )
    return sorted(images)

def getImageItem( image ):
    ext = os.path.splitext( image )[-1]
    cls = IMAGE_MAPPING.get(ext.lower()) or PV_ImageItem
    return cls(image)


def groupImagesByDay( image_items ):
    groups = {}
    for image in image_items:
        value = image.datetime.date().isoformat()
        if value not in groups:
            groups[value] = PV_DateGroupItem( value )
        group = groups[value]
        group.addChild( image )
    return sorted(groups.values(), key=lambda group: group.datetime)

def isContinuousShooting( a, b ):
    if not isinstance( a, PV_ImageItem ) or not isinstance( b, PV_ImageItem ):
        return False
    
    # Sequencial image (based on naming)
    #   check sequence_number
    m1 = re.search('[0-9]+', a.name)
    m2 = re.search('[0-9]+', b.name)
    if m1 and m2 and (int(m2.group()) - int(m1.group()) == 1):
        return b.sequence_number - a.sequence_number == 1

    # Not sequencial image name
    #  - check threshold sec
    #  - sequence_number is not the same (not best, but more for sanity check)
    threshold = int(config.data.get('continuous_shoot_threshold_sec')) or 1
    diff = (b.datetime - a.datetime).seconds
    if diff > threshold:
        return False
    return a.sequence_number != b.sequence_number
            
    
def groupImagesByContinuousShooting( images ):
#    threshold = int(config.data.get('continuous_shoot_threshold_sec')) or 1
    groups = []

    prev_image = None
    curr_group = None
    
    for curr_image in images:
        if not prev_image:
            prev_image = curr_image
            continue

        #if abs(prev_image.datetime - curr_image.datetime).seconds < threshold:
        if isContinuousShooting( prev_image, curr_image ):
            if not curr_group:
                curr_group = PV_ContinuousShootGroupItem( prev_image.datetime )
                groups.append( curr_group )
                
            if prev_image.parent:
                prev_image.parent.addChild( curr_group )
            if curr_image.parent:
                curr_image.parent.addChild( curr_group )
            curr_group.addChild( prev_image )
            curr_group.addChild( curr_image )

        elif curr_group:
            curr_group = None

            
        prev_image = curr_image
        
    return groups
    
def test_populateItems():
    images = findImages()
    image_items = [ImageItem(image) for image in images]
    date_groups = groupImagesByDay( image_items )
    cs_groups = groupImagesByContinuousShooting( image_items )
    return image_items, cs_groups, date_groups
    
