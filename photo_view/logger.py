import logging

def getLogger():
    logger = logging.getLogger('PHOTO_VIEW')
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel( logging.INFO )
        formatter = logging.Formatter( '%(name)s %(levelname)s: %(message)s' )
        ch.setFormatter( formatter )
        logger.addHandler( ch )
        logger.setLevel( logging.INFO )
    return logger

logger = getLogger()

def setDebug( value = True ):
    if value:
        logger.setLevel( logging.DEBUG )
        logger.handlers[0].setLevel( logging.DEBUG )
        logger.handlers[0].formatter._fmt = '%(name)s %(levelname)s (%(module)s %(funcName)s): %(message)s'
    else:
        logger.setLevel( logging.INFO )
        logger.handlers[0].setLevel( logging.INFO )
        logger.handlers[0].formatter._fmt = '%(name)s %(levelname)s: %(message)s'
