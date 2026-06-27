from xml.etree import ElementTree as ET  # noqa: N817

from plugin.managers.report_manager import ReportManager


def test_default_report_is_valid_atom_error_xml():
    root = ET.fromstring(ReportManager.default())

    assert root.tag == 'columns'

    messages = root.findall('message')
    assert len(messages) == 2
    assert messages[0].get('text') == 'Absorption correction failed!'
    assert messages[1].get('text') == 'Open `${ATOM_PATH}/Data/.log` to more information'
