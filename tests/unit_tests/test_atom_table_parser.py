from base64 import b64encode
from xml.etree.ElementTree import Element, SubElement

import numpy as np

from plugin.managers.data_source_manager.data_sources.xml_data_source.parsers.atom_table_parser import AtomTableParser


def test_table_parser_applies_bad_mask_to_peak_intensity_and_value():
    root = Element('root')

    columns = SubElement(root, 'columns')
    sheet = SubElement(columns, 'sheet')
    column = SubElement(sheet, 'column', id='0', name='Ag 338.289', type='line', visible='yes')
    cells = SubElement(column, 'cells')
    SubElement(cells, 'pc', i='sample', cm='1.0')

    probes = SubElement(root, 'probes')
    probe = SubElement(probes, 'probe', id='sample', name='Sample', visible='yes')
    spe = SubElement(probe, 'spe', name='parallel', disabled='no')
    graph = SubElement(SubElement(spe, 'graphs'), 'graph', id='0')

    value = np.array([1.0, 5.0, 3.0], dtype=np.float32)
    yvals = SubElement(graph, 'yvals', value_array_size='3')
    yvals.text = b64encode(value.tobytes()).decode('ascii')

    bad = np.array([1], dtype=np.int32)
    SubElement(graph, 'bad').text = b64encode(bad.tobytes()).decode('ascii')

    data = AtomTableParser.from_xml(root)
    frame = data['0'].frame

    assert frame.loc[('Sample', 'parallel'), 'intensity'] == 3.0
    np.testing.assert_allclose(
        frame.loc[('Sample', 'parallel'), 'value'],
        np.array([1.0, np.nan, 3.0]),
    )
