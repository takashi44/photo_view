from PySide6 import QtCore
from PySide6 import QtGui

from .item import *
from . import config
from . import pathutil
from .logger import logger

import os

class PV_Model( QtCore.QAbstractItemModel ):

    checkStateChanged = QtCore.Signal( QtCore.QModelIndex )
    
    def __init__( self, parent = None ):
        super( PV_Model, self ).__init__( parent )
        self.root_nodes = self._getRootNodes()
        self._populateNodes()

        icon_img = pathutil.resolvePackagePath( config.data['folder_icon'] )
        self.folder_icon = QtGui.QIcon( icon_img )
        icon_img = pathutil.resolvePackagePath( config.data['continuous_shoot_icon'] )
        self.cs_icon = QtGui.QIcon( icon_img )

    def rowCount( self, index ):
        if index.isValid():
            return len(index.internalPointer().children)
        return len(self.root_nodes)

    def columnCount( self, index ):
        return 1

    def index( self, row, column, parent=None ):
        if not parent or not parent.isValid():
#            logger.debug('row: %d' % row )
            if row < len(self.root_nodes):
                return self.createIndex(row, column, self.root_nodes[row] )

        if not self.hasIndex( row, column, parent ):
            return QtCore.QModelIndex()
        
        parent_node = parent.internalPointer()

        if parent_node.children:
            return self.createIndex( row, column, parent_node.children[row] )
        return QtCore.QModelIndex()

    def parent( self, index ):
        if not index.isValid():
            return QtCore.QModelIndex()
        node = index.internalPointer()
        if node.parent:
            return self.createIndex( node.parent.children.index(node), 0, node.parent )
        else:
            return QtCore.QModelIndex()

    def data( self, index, role = QtCore.Qt.DisplayRole ):
        if not index.isValid():
            return None

        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.name

        elif role == QtCore.Qt.DecorationRole:
            if isinstance(node, PV_ImageItem):
                pm = QtGui.QPixmap()
                key = 'icon_' + node.name
                if not QtGui.QPixmapCache.find( key, pm ):
                    pm.loadFromData( node.thumbnail )
                    QtGui.QPixmapCache.insert( key, pm )
                return QtGui.QIcon(pm)
            elif isinstance(node, PV_ContinuousShootGroupItem ):
                return self.cs_icon
            return self.folder_icon

        elif role == QtCore.Qt.CheckStateRole:
            if node not in self.root_nodes:
                if getattr(node, 'checked', 0):
                    return QtCore.Qt.Checked
                return QtCore.Qt.Unchecked
        
    def headerData( self, section, orientation, role=QtCore.Qt.DisplayRole ):
        if section == 0 and role == QtCore.Qt.Orientation:
            return 'Name'
        return None

    def reset( self ):
        self.beginResetModel()
        self.root_nodes = self._getRootNodes()
        self._populateNodes()
        self.endResetModel()

    def flags( self, index ):
        if index.isValid():
            return (QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable)
        
        return super(PV_Model, self ).flags(index)

    def setData( self, index, value, role=QtCore.Qt.EditRole ):
        if not index.isValid():
            return False

        node = index.internalPointer()
        if role == QtCore.Qt.CheckStateRole:
            if getattr(node, 'checked', 0) != value:
                node.checked = value
                self.dataChanged.emit(index, index)
                self.checkStateChanged.emit(index)
            return True

    def getChildren( self, index, recursive=True ):
        indexes = []
        for i in range( self.rowCount( index ) ):
            child = self.index( i, 0, index )
            indexes.append( child )
            if recursive:
                indexes.extend( self.getChildren( child, True ) )
        return indexes
            

    def _getRootNodes( self ):
        nodes = []
        root_dirs = config.data['image_root_dirs']
        for root_dir in root_dirs:
            if os.path.exists( root_dir ):
                node = PV_RootItem( root_dir )
                nodes.append( node )
        return nodes

    def _populateNodes( self ):
        for root_node in self.root_nodes:
            images = findImages( root_node.data )
            items = []
            for image in images:
                try:
                    item = getImageItem(image)
                    items.append(item)
                except Exception as err:
                    logger.error(err)

            dates = groupImagesByDay( items )
            css = groupImagesByContinuousShooting( items )
            for item in dates:
                root_node.addChild(item)
            
    def removeRows( self, row, count, parent=QtCore.QModelIndex() ):
        logger.debug('removeRows()...%d, %d' % (row, count))
        if not parent.isValid():
            return False
        
        node = parent.internalPointer()
        if row >= len(node.children):
            return False

        self.beginRemoveRows(parent, row, row+count-1)
        children = node.children[row:row+count]
        for child in children:
            node.removeChild( child )
        self.endRemoveRows()
        return True
