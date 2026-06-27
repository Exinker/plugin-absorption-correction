from collections.abc import Callable, Mapping
from typing import Protocol

from plugin.dto import AtomDatum
from spectrumlab.types import Frame, R


class CorrectionPreview(Protocol):

    def show(
        self,
        data: Mapping[str, AtomDatum],
        update_callback: Callable[[str, Frame, tuple[R, R] | None], tuple[tuple[R, R], Frame]],
        dump_callback: Callable[[], None],
    ) -> None:
        pass
