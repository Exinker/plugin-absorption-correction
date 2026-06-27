"""Atom plugin to process absorption signals."""

import os
import sys
import warnings
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).parents[2].resolve()

from .plugin import Plugin

warnings.filterwarnings('ignore')


__name__ = 'plugin-absorption-correction'
__version__ = version('plugin')
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
