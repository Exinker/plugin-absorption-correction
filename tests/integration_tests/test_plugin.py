from pathlib import Path
from xml.etree import ElementTree as ET  # noqa: N817

import numpy as np

import pytest

from plugin import Plugin
from tests.fakes import HeadlessCorrectionPreview


@pytest.fixture()
def result(
    filepath: Path,
) -> str | None:
    plugin = Plugin.create(
        correction_preview=HeadlessCorrectionPreview(),
    )
    return plugin.run('<input>{path}</input>'.format(
        path=filepath,
    ))


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
    assert np.isclose(float(__bounds.get('lb')), 0.005226304056122899)
    assert np.isclose(float(__bounds.get('ub')), 0.012719502858817577)

    __point = __column.findall('polynom/point')[-1]
    x = float(__point.get('x'))
    y = float(__point.get('y'))
    assert np.isclose(x, 3.6337552070617676)
    assert np.isclose(y, 755.6614320252214)
