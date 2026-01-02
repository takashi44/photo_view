import yaml
import os
import pathlib
import getpass
from .logger import logger
from . import pathutil


__path = pathutil.resolvePackagePath('etc/config.yml')
data = {}


def load():
    global data
    with open( __path ) as fp:
        logger.info('Loading default config from: %s' % __path )
        data = yaml.safe_load( fp )
    data = _expand_paths( data )
    return data

def _expand_paths( value ):
    if isinstance( value, str ):
        expanded = value.replace('{username}', getpass.getuser())
        expanded = os.path.expandvars( os.path.expanduser( expanded ) )
        return expanded
    if isinstance( value, list ):
        return [ _expand_paths( item ) for item in value ]
    if isinstance( value, dict ):
        return { key: _expand_paths( item ) for key, item in value.items() }
    return value
    
def update( **kwargs ):
    global data
    if not data:
        data = load()
    for key, value in kwargs.items():
        data[key] = value
    return data

def save( path=None ):
    global data
    if not path:
        path = __path
    if data:
        with open( path, 'w' ) as fp:
            yaml.dump( data, fp )
    return path

data = load()
