import logging
import time

from plugin.dto import AtomData
from plugin.managers.data_source_manager.data_sources import DataSource

LOGGER = logging.getLogger('plugin-absorption-correction')


class DataSourceManager:

    def __init__(
        self,
        data_source: DataSource,
    ) -> None:
        self.data_source = data_source

    def load(self) -> AtomData:
        started_at = time.perf_counter()

        LOGGER.info(
            'Start loading data with data source %s',
            self.data_source.__class__.__name__,
        )

        atom_data = self.data_source.load()
        LOGGER.info(
            'Atom data loaded successfully',
            extra=dict(
                filepath=atom_data.filepath,
                columns=len(atom_data.data),
                time_elapsed=time.perf_counter() - started_at,
            ),
        )
        return atom_data
