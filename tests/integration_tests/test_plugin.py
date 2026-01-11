from pathlib import Path
from xml.etree import ElementTree as ET  # noqa: N817

import numpy as np

import pytest
from PySide6 import QtCore

from plugin import Plugin


@pytest.fixture(scope='module')
def result(
    filepath: Path,
    qapp,
) -> str | None:
    result = None

    def run_plugin():
        nonlocal result

        plugin = Plugin.create()
        result = plugin.run('<input>{path}</input>'.format(
            path=filepath,
        ))
        qapp.quit()

    def close_plugin():
        for widget in qapp.topLevelWidgets():
            if widget.isWindow() and widget.isVisible():
                widget.close()

    QtCore.QTimer.singleShot(100, run_plugin)
    QtCore.QTimer.singleShot(5000, close_plugin)

    return result


def test_transformer(
    column_id: str,
    column_name: str,
    result: str | None,
):

    assert result is not None
    root = ET.fromstring(result)

    __column = root.find('column')
    assert __column.get('id') == column_id
    assert __column.get('nickname') == column_name

    __bounds = __column.find('bounds')
    assert np.isclose(float(__bounds.get('lb')), 0.0063353106)
    assert np.isclose(float(__bounds.get('ub')), 0.023939835)

    __point = __column.findall('polynom/point')[-1]
    x = float(__point.get('x'))
    y = float(__point.get('y'))
    assert np.isclose(x, 3.633622646331787)
    assert np.isclose(y, 798.6390840260021)
