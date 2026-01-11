from typing import Self

from plugin.config import PLUGIN_CONFIG
from plugin.exceptions import exception_wrapper
from plugin.managers.correction_manager import CorrectionManager
from plugin.managers.data_manager import DataManager
from plugin.managers.report_manager import ReportManager
from plugin.types import XML


class Plugin:

    @classmethod
    def create(cls) -> Self:

        data_manager = DataManager()
        correction_manager = CorrectionManager(
            plugin_config=PLUGIN_CONFIG,
        )
        report_manager = ReportManager(
            plugin_config=PLUGIN_CONFIG,
        )

        return Plugin(
            data_manager=data_manager,
            correction_manager=correction_manager,
            report_manager=report_manager,
        )

    def __init__(
        self,
        data_manager: DataManager,
        correction_manager: CorrectionManager,
        report_manager: ReportManager,
    ) -> None:

        self.data_manager = data_manager
        self.correction_manager = correction_manager
        self.report_manager = report_manager

    @exception_wrapper
    def run(
        self,
        xml: XML,
    ) -> str:

        atom_data = self.data_manager.parse(
            xml=xml,
        )
        transformers = self.correction_manager.retrieve(
            data=atom_data.data,
        )
        report = self.report_manager.build(
            data=atom_data.data,
            transformers=transformers,
            dump=True,
        )

        return report
