from xml.etree import ElementTree as ET  # noqa: N817

import numpy as np

from plugin import Plugin
from tests.fakes import HeadlessCorrectionPreview


def test_plugin_run_returns_atom_report_xml(
    atom_config_xml: str,
    column_id: str,
    column_name: str,
):
    result = Plugin.create(
        correction_preview=HeadlessCorrectionPreview(),
    ).run(atom_config_xml)
    root = ET.fromstring(result)

    assert root.tag == 'columns'

    column = root.find('column')
    assert column is not None
    assert column.get('id') == column_id
    assert column.get('nickname') == column_name

    bounds = column.find('bounds')
    assert bounds is not None
    assert np.isclose(float(bounds.get('lb')), 0.005226304056122899)
    assert np.isclose(float(bounds.get('ub')), 0.012719502858817577)

    point = column.findall('polynom/point')[-1]
    x = float(point.get('x'))
    y = float(point.get('y'))
    assert np.isclose(x, 3.6337552070617676)
    assert np.isclose(y, 755.6614320252214)
