import yaml
import os
import pathlib
from .logger import logger
from . import pathutil


__path = pathutil.resolvePackagePath('etc/config.yml')
data = {}


def load():
    global data
    with open( __path ) as fp:
        logger.info('Loading default config from: %s' % __path )
        data = yaml.safe_load( fp )
    return data
    
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
