from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui

from .item import PV_ImageItem, PV_ContinuousShootGroupItem
from . import config
from .model  import PV_Model
from . import pathutil
from .logger import logger

import os
import shutil
import filecmp

QtGui.QPixmapCache.setCacheLimit( config.data.get('pixmap_cache_size') or 10240*100 )

class PV_Label( QtWidgets.QLabel ):
    doubleClicked = QtCore.Signal()
    def mouseDoubleClickEvent( self, event ):
        self.doubleClicked.emit()

        
class PV_TreeView( QtWidgets.QTreeView ):
    def __init__( self, parent=None ):
        super( PV_TreeView, self ).__init__( parent )
        icon_size = config.data.get('icon_size') or 32
        self.setIconSize( QtCore.QSize( icon_size, icon_size ) )
        self.setSelectionMode( QtWidgets.QAbstractItemView.ExtendedSelection )
        
class PV_MainWindow( QtWidgets.QMainWindow ):

    def __init__( self, parent=None ):
        super( PV_MainWindow, self ).__init__( parent )
        self.setWindowTitle('Photo Image Manager')
        main_layout = QtWidgets.QGridLayout()
        main_widget = QtWidgets.QWidget(self)
        main_widget.setLayout( main_layout )
        self.setCentralWidget( main_widget )
        
        self.tree_view = PV_TreeView( self )
        self.model = PV_Model(self)
        self.tree_view.setModel( self.model )
        self.scroll_area = QtWidgets.QScrollArea( self )
        #self.image_label = QtWidgets.QLabel()
        self.image_label = PV_Label()
        self.image_label.setBackgroundRole( QtGui.QPalette.Base )
        self.scroll_area.setBackgroundRole( QtGui.QPalette.Dark )
        self.scroll_area.setWidget( self.image_label )

        splitter = QtWidgets.QSplitter( QtCore.Qt.Horizontal, self )
        splitter.addWidget( self.tree_view )
        splitter.addWidget( self.scroll_area )
        splitter.setSizes( [100, 200] )
        
        button_box = QtWidgets.QDialogButtonBox( self )
        close_button  = button_box.addButton('Close'       , QtWidgets.QDialogButtonBox.RejectRole )
        copy_button   = button_box.addButton('Copy/Import' , QtWidgets.QDialogButtonBox.ActionRole )
        delete_button = button_box.addButton('Delete'      , QtWidgets.QDialogButtonBox.ActionRole )

        main_layout.addWidget( splitter, 0, 0, 1, 1 )
        main_layout.addWidget( button_box, 1, 0, 1, 1 )

        close_button.clicked.connect( self.close )
        copy_button.clicked.connect( self.copy )
        delete_button.clicked.connect( self.delete )
        
        self.model.checkStateChanged.connect( self.updateCheckboxes )
        self.tree_view.selectionModel().currentChanged.connect( self.updatePreview )
        splitter.splitterMoved.connect( self.adjustPreviewSize )
        self.tree_view.doubleClicked.connect( self.treeDoubleClicked )
        self.image_label.doubleClicked.connect( self.previewDoubleClicked )
        
        self.resize( 1024, 1024 )
        
        QtGui.QShortcut( QtGui.QKeySequence('return'), self.tree_view, self.toggle )
        QtGui.QShortcut( QtGui.QKeySequence('f'), self, self.fitPreviewImageToWindow )
        QtGui.QShortcut( QtGui.QKeySequence('Ctrl+1'), self, self.scale100 )
        QtGui.QShortcut( QtGui.QKeySequence('backspace'), self, self.delete )
                             
        #
        # Menu
        # 
        option_menu = self.menuBar().addMenu('Options')
        self.auto_fit_action = option_menu.addAction('Auto Fit Preview')
        self.auto_fit_action.setCheckable( True )
        self.auto_fit_action.setChecked( True )
        option_menu.addSeparator()
        scale100_action = option_menu.addAction('Scale 100%')
        scale100_action.triggered.connect( self.scale100 )
        scale100_action.setShortcut( '1' )
        scale200_action = option_menu.addAction('Scale 200%')
        scale200_action.triggered.connect( self.scale200 )
        scale200_action.setShortcut( '2' )
        scale050_action = option_menu.addAction('Scale 50%')
        scale050_action.triggered.connect( self.scale050 )
        scale050_action.setShortcut( 'Ctrl+2' )
        option_menu.addSeparator()
        reset_action = option_menu.addAction('Reset')
        reset_action.triggered.connect( self.resetModel )
        reset_action.setShortcut('Ctrl+r')

    def treeDoubleClicked( self, index ):
        if not index.isValid():
            return
        node = index.internalPointer()
        if isinstance( node, PV_ImageItem ):
            os.system( 'open %s' % node.data )

    def previewDoubleClicked( self, *args ):
        index = self.tree_view.currentIndex()
        node = index.internalPointer()
        if isinstance( node, PV_ImageItem ):
            os.system( 'open %s' % node.data )


    def updatePreview( self, *args ):
        logger.debug('updatePreview()...')
        index = self.tree_view.currentIndex()
        node = index.internalPointer()
        if node:
            logger.debug('  name: %s' % node.name )
        fit = self.auto_fit_action.isChecked()
        self.showPreviewImage( node, fit )

    def getPixmap( self, node ):
        if not node:
            return
        logger.debug('getPixmap()... %s' % node.name )
        pm = QtGui.QPixmap()
        key = node.name
        if not QtGui.QPixmapCache.find( key, pm ):
            if isinstance( node, PV_ImageItem ):
                pm.loadFromData( node.preview )
                pm = orientPixmap( pm, node.orientation )
            elif isinstance( node, PV_ContinuousShootGroupItem ):
                pm  = self.compositeSeqImages( node )
            QtGui.QPixmapCache.insert( key, pm )
        else:
            logger.debug('Hit from cache: %s' % key )
        return pm
        

    def compositeSeqImages( self, node ):
        logger.debug('compositeSeqImages()...%s' % node.name)
        child = node.children[0]
        pixmap = self.getPixmap( child )
        out_image = QtGui.QImage( pixmap.size(), QtGui.QImage.Format_ARGB32_Premultiplied )

        source_size = pixmap.size()
        dest_size =  source_size + QtCore.QSize( 100, 100 )
        out_image = QtGui.QImage( dest_size, QtGui.QImage.Format_ARGB32_Premultiplied )

        brush = QtGui.QBrush( QtCore.Qt.gray, QtCore.Qt.SolidPattern )
        painter = QtGui.QPainter()
        painter.begin( out_image )
        painter.setCompositionMode( QtGui.QPainter.CompositionMode_Source )

        painter.setBrush( brush )
        painter.drawRoundedRect( 90, 90, source_size.width(), source_size.height(), 5.0, 5.0 )
        painter.drawRoundedRect( 60, 60, source_size.width(), source_size.height(), 5.0, 5.0 )
        painter.drawRoundedRect( 30, 30, source_size.width(), source_size.height(), 5.0, 5.0 )

        painter.drawPixmap( 0, 0, pixmap )
        painter.end()
        
        return QtGui.QPixmap.fromImage( out_image, QtCore.Qt.AutoColor )

    def showPreviewImage( self, node, fit=False, scale=100 ):
        pm = self.getPixmap( node )
        if not bool(pm):
            self.image_label.clear()
            return

        scale_size = None
        if fit:
            scale_size = self.scroll_area.size()
        elif scale != 100:
            scale_size = pm.size() * scale / 100.0

        if scale_size:
            pm = pm.scaled( scale_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation )
                
        self.image_label.setPixmap( pm )
        self.image_label.adjustSize()
        
        
    def updateCheckboxes( self, *args ):
        logger.debug('updateCheckboxes()...')
        curr = args[0]
        node = curr.internalPointer()
        model = self.tree_view.model()

        if model.rowCount( curr ) > 0:
            self.updateDecendantCheckboxes( curr )
            
        selected = self.tree_view.selectedIndexes()
        if curr not in selected:
            return
        
        # multi selection
        logger.debug('Num of selected: %d' % len(selected) )
        for index in selected:
            item = index.internalPointer()
            item.checked = node.checked
            model.dataChanged.emit(index, index)
            if model.rowCount( index ) > 0:
                self.updateDecendantCheckboxes( index )
                
    def updateDecendantCheckboxes( self, index ):
        model = self.tree_view.model()
        node = index.internalPointer()
        children = model.getChildren( index )
        for child in children:
            child.internalPointer().checked = node.checked
            model.dataChanged.emit(child, child)                


    def getCheckedIndexes( self ):
        model = self.tree_view.model()
        indexes = model.match( model.index(0, 0),
                               QtCore.Qt.CheckStateRole,
                               QtCore.Qt.Checked,
                               -1,
                               QtCore.Qt.MatchRecursive )
        return indexes

    def getCheckedImages( self, check_error=True ):
        indexes = self.getCheckedIndexes()
        nodes = [index.internalPointer() for index in indexes]
        nodes = [node for node in nodes if isinstance( node, PV_ImageItem)]

        if check_error:
            if not nodes:
                QtWidgets.QMessageBox.critical(self, "No Image Checked", "No Image Checked")
                raise RuntimeError
            
        logger.debug('%d items checked' % len(nodes))
        
        return nodes

    def copy( self, *args ):
        logger.debug('Copy()...')
        nodes = self.getCheckedImages()
        rel_paths = [node.path for node in nodes]

        save_folder = config.data['image_save_folder']
        folder = QtWidgets.QFileDialog.getExistingDirectory( self,
                                                             'Select Destination Folder',
                                                             save_folder,
                                                             (QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks) )

        if not folder:
            return
        
        logger.debug('Dest folder: %s' % folder )
        if not os.path.exists( folder ):
            raise RuntimeError('Invalid path: %s' % folder )

        self.model.setImportDestination( folder )

        dest_paths = [os.path.join(folder, rel_path) for rel_path in rel_paths]
        action = 'skip'
        if any([os.path.exists(path) for path in dest_paths] ):
            msg = QtWidgets.QMessageBox()
            msg.setText('Some images already exist')
            replace_button = msg.addButton('Replace', QtWidgets.QMessageBox.YesRole)
            skip_button = msg.addButton('Skip', QtWidgets.QMessageBox.NoRole)
            cancel_button = msg.addButton('Cancel', QtWidgets.QMessageBox.RejectRole)
            msg.exec_()
            clicked = msg.clickedButton()
            if clicked == cancel_button:
                return
            if clicked == replace_button:
                action = 'replace'
            else:
                action = 'skip'
            logger.debug('existing file action: %s' % action )

        src_paths = [node.data for node in nodes]

        progress = QtWidgets.QProgressDialog("Copy Images", "Cancel", 0, len(nodes), self )
        progress.setWindowModality( QtCore.Qt.WindowModal )
        progress.show()
        
        for i, (src, dst) in enumerate(zip(src_paths, dest_paths)):
            progress.setValue(i)
            if progress.wasCanceled():
                break
            
            if not os.path.exists(os.path.dirname(dst)):
                os.mkdir( os.path.dirname(dst) )

            if os.path.exists( dst ):
                if action == 'replace':
                    os.remove( dst )
                else:
                    continue
            logger.debug('Copying from %s to %s' % (src, dst))
            shutil.copy2( src, dst )

        progress.setValue(len(nodes))
        self.model.refreshImportStatus()
        

    def delete( self, *args ):
        logger.debug('Delete()...')
        indexes = self.getCheckedIndexes()

        nodes = [index.internalPointer() for index in indexes]
        nodes = [node for node in nodes if isinstance( node, PV_ImageItem)]

        if not nodes:
            return
        
        ret = QtWidgets.QMessageBox.warning(self, 'Delete' , 'Deleting %d images' % len(nodes),
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel )
        if ret != QtWidgets.QMessageBox.Yes:
            return

        model = self.tree_view.model()

        indexes.sort( key=lambda item: item.row(), reverse=True )

        parents = set()
        for index in indexes:

            # remove the item from the model
            parent = index.parent()
            logger.debug('removeRow: %s row:%d, parent:%s' % (model.data(index), index.row(), model.data(parent)))
            ret = model.removeRow( index.row(), parent )
            logger.debug( "removeRow: %s" % str(ret) )
            # if parent has no children, remove from the model later
            if not parent.internalPointer().children:
                parents.add( parent )

            # actually deleting image file
            node = index.internalPointer()
            if isinstance( node, PV_ImageItem ):
                logger.debug('Deleting %s' % node.data )
                os.remove( node.data )

        # clean up groups with no children
        logger.debug('Parents with no child: %d' % len(parents))
        parents = list(parents)
        parents.sort( key=lambda item: item.row(), reverse=True )
        for index in parents:
            if index in indexes:
                continue
            
            node = index.internalPointer()
            if not node.children:
                logger.debug("removeRow(parent): %s" % model.data(index) )
                ret = model.removeRow( index.row(), index.parent() )
                logger.debug("removeRow(parent): %s" % str(ret) )
        

    def toggle( self, *args ):
        logger.debug('Toggle()...')

        if self.tree_view.hasFocus():
            index = self.tree_view.currentIndex()
            if not index.isValid():
                return
            checked = self.tree_view.model().data( index, QtCore.Qt.CheckStateRole )
            new_value = QtCore.Qt.Checked
            if checked:
                new_value = QtCore.Qt.Unchecked

            self.tree_view.model().setData( index, new_value, QtCore.Qt.CheckStateRole )

    def resizeEvent( self, event ):
        logger.debug('resizeEvent()...')
        super( PV_MainWindow, self ).resizeEvent( event )
        self.adjustPreviewSize()

    def adjustPreviewSize( self, *args ):
        if self.auto_fit_action.isChecked():
            self.fitPreviewImageToWindow()

    def fitPreviewImageToWindow( self, *args ):
        logger.debug('fitPreviewImageToWindow()...')
        index = self.tree_view.currentIndex()
        node = index.internalPointer()
        self.showPreviewImage( node, True )

    def scalePreviewImage( self, scale ):
        logger.debug('scalePreviewImage()...')
        index = self.tree_view.currentIndex()
        node = index.internalPointer()
        self.showPreviewImage( node, False, scale )
        
    def scale100( self, *args ):
        self.scalePreviewImage( 100 )

    def scale200( self, *args ):
        self.scalePreviewImage( 200 )

    def scale050( self, *args ):
        self.scalePreviewImage( 50 )

    def resetModel( self, *args ):
        self.tree_view.model().reset()
        
        


def orientPixmap( pixmap, exif_orientation ):
    if exif_orientation == 2:
        pixmap = pixmap.transformed( QtGui.QTransform().scale(-1, 1) )
    elif exif_orientation == 3:
        pixmap = pixmap.transformed( QtGui.QTransform().rotate( 180 ) )
    elif exif_orientation == 4:
        pixmap = pixmap.transformed( QtGui.QTransform().rotate( 180 ) )
        pixmap = pixmap.transformed( QtGui.QTransform().scale(-1, 1) )
    elif exif_orientation == 5:
        pixmap = pixmap.transformed( QtGui.QTransform().rotate( 90 ) )
        pixmap = pixmap.transformed( QtGui.QTransform().scale(-1, 1) )
    elif exif_orientation == 6:
        pixmap = pixmap.transformed( QtGui.QTransform().rotate( 90 ) )
    elif exif_orientation == 7:
        pixmap = pixmap.transformed( QtGui.QTransform().rotate( 270 ) )
        pixmap = pixmap.transformed( QtGui.QTransform().scale(-1, 1) )
    elif exif_orientation == 8:
        pixmap = pixmap.transformed( QtGui.QTransform().rotate( 270 ) )

    return pixmap


        
