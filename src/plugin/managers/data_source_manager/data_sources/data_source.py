from typing import Protocol

from plugin.dto import AtomData
from plugin.types import XML


class DataSource(Protocol):

    def load(self, xml: XML | None = None) -> AtomData:
        pass
