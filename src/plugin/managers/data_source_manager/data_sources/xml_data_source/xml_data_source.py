import logging
import time

from plugin.dto import AtomData
from plugin.managers.data_source_manager.data_sources.exceptions import (
    DataSourceError,
    LoadDataXMLError,
    ParseDataXMLError,
    ParseFilepathXMLError,
)
from plugin.managers.data_source_manager.data_sources.xml_data_source.parsers import (
    AtomDataParser,
    FilepathParser,
)
from plugin.types import XML

LOGGER = logging.getLogger('plugin-absorption-correction')


class XMLDataSource:

    def __init__(
        self,
        xml: XML,
    ) -> None:

        self.xml = xml

    def load(self) -> AtomData:
        started_at = time.perf_counter()

        LOGGER.info('Start data loading from XML')
        try:
            filepath = FilepathParser.parse(self.xml)

        except ParseFilepathXMLError as error:
            LOGGER.error(
                'Failed to load data',
                extra=dict(
                    error=error,
                ),
            )
            raise

        else:
            LOGGER.info('Filepath to data: %r', filepath)

        finally:
            LOGGER.info(
                'Data loaded successfully',
                extra=dict(
                    time_elapsed=time.perf_counter() - started_at,
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
            LOGGER.info(
                'Data loaded successfully',
                extra=dict(
                    time_elapsed=time.perf_counter() - started_at,
                ),
            )
