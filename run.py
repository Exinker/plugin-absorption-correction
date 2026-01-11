import logging
from argparse import ArgumentParser

import plugin
from plugin import Plugin
from plugin.config import PLUGIN_CONFIG
from plugin.loggers import *
from plugin.types import XML


LOGGER = logging.getLogger('plugin-absorption-correction')
PLUGIN = Plugin.create()


def process_xml(config_xml: XML) -> str:

    LOGGER.info('run %r', plugin.__name__)
    LOGGER.info('PLUGIN_CONFIG: %s', PLUGIN_CONFIG)

    return PLUGIN.run(config_xml)


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument(
        '--config',
        help='XML with config',
        default=r'<input>C:\Atom x64 3.3 (2025.11.14)\Temp\py_table.xml</input>',
    )
    args = parser.parse_args()

    result = process_xml(
        config_xml=args.config,
    )
    print(result)
