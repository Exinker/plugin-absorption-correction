import logging
import time

from plugin.dto import AtomData
from plugin.managers.data_manager.data_sources import DataSource
from plugin.types import XML


LOGGER = logging.getLogger('plugin-absorption-correction')


class DataSourceManager:

    def __init__(
        self,
        data_source: DataSource,
    ) -> None:
        self.data_source = data_source

    def load(self, xml: XML | None = None) -> AtomData:
        started_at = time.perf_counter()

        LOGGER.info(
            'Start loading atom data: data_source=%s',
            self.data_source.__class__.__name__,
        )

        atom_data = self.data_source.load(xml=xml)

        LOGGER.info(
            'Atom data loaded: filepath=%r, columns=%d, elapsed=%.4f, s',
            atom_data.filepath,
            len(atom_data.data),
            time.perf_counter() - started_at,
        )

        return atom_data
