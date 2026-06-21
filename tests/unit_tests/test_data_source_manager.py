from plugin.dto import AtomData, AtomFilepath, AtomMeta
from plugin.managers.data_manager import DataSourceManager


class FakeDataSource:

    def __init__(self, data: AtomData) -> None:
        self.data = data
        self.xml = None

    def load(self, xml=None) -> AtomData:
        self.xml = xml
        return self.data


def test_data_source_manager_delegates_parse():
    atom_data = AtomData(
        filepath=AtomFilepath('data.xml'),
        meta=AtomMeta(
            organization_name='Test Organization',
            device_name='Test Device',
            user_name='Test User',
            analysis_name='Test Analysis',
        ),
        data={},
    )
    data_source = FakeDataSource(data=atom_data)
    manager = DataSourceManager(data_source=data_source)

    result = manager.load(xml='<input>data.xml</input>')

    assert result is atom_data
    assert data_source.xml == '<input>data.xml</input>'
