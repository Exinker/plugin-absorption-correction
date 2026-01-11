"""Atom plugin to process absorption signals."""

import warnings
warnings.filterwarnings('ignore')

from datetime import datetime

import pkg_resources

from .plugin import Plugin



distribution = pkg_resources.get_distribution('plugin')
__name__ = 'plugin-absorption-correction'
__version__ = distribution.version
__author__ = 'Pavel Vaschenko'
__email__ = 'vaschenko@vmk.ru'
__organization__ = 'VMK-Optoelektronika'
__license__ = 'MIT'
__copyright__ = 'Copyright {}, {}'.format(datetime.now().year, __organization__)

__all__ = [
    Plugin,
]
