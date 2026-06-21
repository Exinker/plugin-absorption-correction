import logging
import time
from pathlib import Path

from plugin.dto import AtomData
from plugin.managers.data_manager.data_sources.exceptions import (
    DataSourceError,
    LoadDataXMLError,
    ParseDataXMLError,
    ParseFilepathXMLError,
)
from plugin.managers.data_manager.data_sources.xml_data_source.parsers import (
    AtomDataParser,
    FilepathParser,
)
from plugin.types import XML


LOGGER = logging.getLogger('plugin-absorption-correction')


class XMLDataSource:

    def load(self, xml: XML | None = None) -> AtomData:
        LOGGER.info('Start XML data source loading.')

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
            raise DataSourceError from error

        else:
            LOGGER.info(
                'XML data source loaded: filepath=%r, columns=%d',
                atom_data.filepath,
                len(atom_data.data),
            )
            return atom_data

        finally:
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(
                    'Time elapsed for data parsing: {elapsed:.4f}, s'.format(
                        elapsed=time.perf_counter() - started_at,
                    ),
                )
