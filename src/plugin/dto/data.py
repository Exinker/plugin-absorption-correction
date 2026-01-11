from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from plugin.dto.filepath import AtomFilepath
from plugin.dto.meta import AtomMeta
from spectrumlab.types import Frame, R


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
