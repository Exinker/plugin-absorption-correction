import logging
from collections.abc import Mapping
from typing import Callable

from PySide6 import QtWidgets

from plugin.dto import AtomDatum
from plugin.managers.correction_manager import CorrectionPreview
from plugin.presentation.windows import PreviewWindow
from spectrumlab.types import Frame, R


LOGGER = logging.getLogger('plugin-absorption-correction')


class QtCorrectionPreview(CorrectionPreview):

    def show(
        self,
        data: Mapping[str, AtomDatum],
        update_callback: Callable[[str, Frame, tuple[R, R] | None], tuple[tuple[R, R], Frame]],
        dump_callback: Callable[[], None],
    ) -> None:
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication()

        window = PreviewWindow(
            data=data,
            update_callback=update_callback,
            dump_callback=dump_callback,
        )
        for column_id, datum in data.items():
            LOGGER.debug(
                'Update window',
                extra=dict(
                    column_id=column_id,
                ),
            )
            window.update(
                column_id=column_id,
                bounds=datum.bounds,
            )

        try:
            app.exec()

        finally:
            app.quit()
