from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui

from . import config
from .logger import logger

logger.warn("==================")
logger.warn("=== DEPRECATED ===")
logger.warn("==================")

class PV_TreeView( QtWidgets.QTreeView ):
    def __init__( self, parent=None ):
        super( PV_TreeView, self ).__init__( parent )
        icon_size = config.data.get('icon_size') or 32
        self.setIconSize( QtCore.QSize( icon_size, icon_size ) )
        self.setSelectionMode( QtWidgets.QAbstractItemView.ExtendedSelection )
