from plugin.dto import AtomData, AtomFilepath, AtomMeta
from plugin.managers.data_source_manager import DataSourceManager


class FakeDataSource:

    def __init__(self, data: AtomData) -> None:
        self.data = data

    def load(self) -> AtomData:
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

    result = manager.load()

    assert result is atom_data
