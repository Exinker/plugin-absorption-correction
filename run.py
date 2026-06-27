import logging
from argparse import ArgumentParser

import plugin
from plugin import Plugin
from plugin.configs import (
    LOGGING_CONFIG,
    PLUGIN_CONFIG,
)
from plugin.loggers import setup_logging
from plugin.managers.data_source_manager.data_sources import XMLDataSource
from plugin.presentation import QtCorrectionPreview
from plugin.types import XML

setup_logging(
    config=LOGGING_CONFIG,
)

LOGGER = logging.getLogger('plugin-absorption-correction')


def process_xml(config_xml: XML) -> str:

    PLUGIN = Plugin.create(
        data_source=XMLDataSource(
            xml=config_xml,
        ),
        preview=QtCorrectionPreview(),
    )

    LOGGER.info('Run plugin %r', plugin.__name__)
    LOGGER.info(
        'Config',
        extra=dict(
            plugin_config=PLUGIN_CONFIG.model_dump(),
            logging_config=LOGGING_CONFIG.model_dump(),
        ),
    )

    return PLUGIN.run()


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument(
        '--config',
        help='config',
        default='<input>{filepath}</input>'.format(
            filepath=PLUGIN_CONFIG.filepath,
        ),
    )
    args = parser.parse_args()

    result = process_xml(
        config_xml=args.config,
    )
    print(result)
