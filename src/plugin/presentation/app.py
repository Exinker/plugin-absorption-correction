import logging
from collections.abc import Mapping
from typing import Callable

from PySide6 import QtWidgets

from plugin.dto import AtomDatum
from plugin.presentation.windows import PreviewWindow
from spectrumlab.types import Frame, R


LOGGER = logging.getLogger('plugin-absorption-correction')


def retrieve_transformer(
    data: Mapping[str, AtomDatum],
    callback: Callable[[tuple[R, R], Frame], Frame],
    quiet: bool = False,
) -> None:

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication()

    window = PreviewWindow(
        data=data,
        callback=callback,
    )
    for column_id, datum in data.items():
        window.update(
            column_id=column_id,
            bounds=datum.bounds,
        )

    try:
        app.exec()
    except Exception:
        raise
    else:
        return None
    finally:
        app.quit()
