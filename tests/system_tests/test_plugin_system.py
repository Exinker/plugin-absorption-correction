from pathlib import Path
from xml.etree import ElementTree as ET  # noqa: N817

import numpy as np

from plugin import Plugin
from plugin.managers.data_source_manager.data_sources import XMLDataSource
from tests.fakes import HeadlessCorrectionPreview


def test_plugin_run_returns_atom_report_xml(
    atom_config_xml: str,
    column_id: str,
    column_name: str,
):
    result = Plugin.create(
        data_source=XMLDataSource(xml=atom_config_xml),
        preview=HeadlessCorrectionPreview(),
    ).run()
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


def test_plugin_run_on_real_py_table_has_no_nan_in_report():
    filepath = Path(__file__).parents[2] / 'py_table.xml'

    result = Plugin.create(
        data_source=XMLDataSource(xml='<input>{path}</input>'.format(path=filepath)),
        preview=HeadlessCorrectionPreview(),
    ).run()
    root = ET.fromstring(result)

    assert 'nan' not in result.lower()

    columns = root.findall('column')
    assert columns

    points = root.findall('.//polynom/point')
    assert points

    for point in points:
        assert np.isfinite(float(point.get('x')))
        assert np.isfinite(float(point.get('y')))
