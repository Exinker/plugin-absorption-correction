"""Atom plugin to process absorption signals."""

import os
import sys
import warnings
from datetime import datetime

import pkg_resources

from .plugin import Plugin


warnings.filterwarnings('ignore')


distribution = pkg_resources.get_distribution('plugin')
__name__ = 'plugin-absorption-correction'
__version__ = distribution.version
__author__ = 'Pavel Vaschenko'
__email__ = 'vaschenko@vmk.ru'
__organization__ = 'VMK-Optoelektronika'
__license__ = 'MIT'
__copyright__ = 'Copyright {}, {}'.format(datetime.now().year, __organization__)


os.environ['APPLICATION_NAME'] = __name__
os.environ['APPLICATION_VERSION'] = __version__
os.environ['ORGANIZATION_NAME'] = __organization__
os.environ['DEPLOY'] = str(hasattr(sys, '_MEIPASS'))


__all__ = [
    Plugin,
]
