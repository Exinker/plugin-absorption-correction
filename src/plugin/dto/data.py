from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from spectrumlab.types import Frame, R

from plugin.dto.filepath import AtomFilepath
from plugin.dto.meta import AtomMeta


@dataclass
class AtomDatum:

    column_id: str
    nickname: str
    frame: Frame
    bounds: tuple[R, R] | None = None
    polynom: Sequence[tuple[R, R]] | None = None


@dataclass
class AtomData:

    filepath: AtomFilepath
    meta: AtomMeta
    data: Mapping[str, AtomDatum]
