import logging
import time
from pathlib import Path

from plugin.dto import AtomData
from plugin.managers.data_manager.exceptions import (
    DataManagerError,
    LoadDataXMLError,
    ParseDataXMLError,
    ParseFilepathXMLError,
)
from plugin.managers.data_manager.parsers import (
    AtomDataParser,
    FilepathParser,
)
from plugin.types import XML


LOGGER = logging.getLogger('plugin-absorption-correction')


class DataManager:

    def parse(self, xml: XML | None = None) -> AtomData:
        xml = xml or '<input>{path}</input>'.format(
            path=str(Path.cwd().parents[3] / 'Temp' / 'py_table.xml'),
        )

        started_at = time.perf_counter()
        try:
            filepath = FilepathParser.parse(xml)

        except ParseFilepathXMLError as error:
            LOGGER.error('%r', error)
            raise

        else:
            LOGGER.info('Filepath to data: %r', filepath)

        finally:
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(
                    'Time elapsed for filepath parsing: {elapsed:.4f}, s'.format(
                        elapsed=time.perf_counter() - started_at,
                    ),
                )

        started_at = time.perf_counter()
        try:
            atom_data = AtomDataParser.parse(filepath)

        except (LoadDataXMLError, ParseDataXMLError) as error:
            raise DataManagerError from error

        else:
            return atom_data

        finally:
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(
                    'Time elapsed for data parsing: {elapsed:.4f}, s'.format(
                        elapsed=time.perf_counter() - started_at,
                    ),
                )
