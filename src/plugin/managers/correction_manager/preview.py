from collections.abc import Callable, Mapping
from typing import Protocol

from spectrumlab.types import Frame, R

from plugin.dto import AtomDatum


class CorrectionPreview(Protocol):

    def show(
        self,
        data: Mapping[str, AtomDatum],
        update_callback: Callable[[str, Frame, tuple[R, R] | None], tuple[tuple[R, R], Frame]],
        dump_callback: Callable[[], None],
    ) -> None:
        pass
