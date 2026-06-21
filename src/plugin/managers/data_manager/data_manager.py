from plugin.dto import AtomData
from plugin.managers.data_manager.data_sources import DataSource
from plugin.types import XML


class DataSourceManager:

    def __init__(
        self,
        data_source: DataSource,
    ) -> None:
        self.data_source = data_source

    def load(self, xml: XML | None = None) -> AtomData:
        return self.data_source.load(xml=xml)
