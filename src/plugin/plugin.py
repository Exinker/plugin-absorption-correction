from typing import Self

from plugin.config import PLUGIN_CONFIG
from plugin.exceptions import exception_wrapper
from plugin.managers.correction_manager import CorrectionPipeline, CorrectionPreview, CorrectionProcessor
from plugin.managers.data_manager.data_sources import XMLDataSource
from plugin.managers.data_manager import DataSourceManager
from plugin.managers.report_manager import ReportManager, XMLReportBuilder
from plugin.types import XML


class Plugin:

    @classmethod
    def create(
        cls,
        correction_preview: CorrectionPreview,
    ) -> Self:

        data_manager = DataSourceManager(
            data_source=XMLDataSource(),
        )
        report_manager = ReportManager(
            plugin_config=PLUGIN_CONFIG,
            report_builder=XMLReportBuilder(),
        )
        correction_pipeline = CorrectionPipeline(
            report_manager=report_manager,
            preview=correction_preview,
            processor=CorrectionProcessor(),
        )

        return Plugin(
            data_manager=data_manager,
            correction_pipeline=correction_pipeline,
            report_manager=report_manager,
        )

    def __init__(
        self,
        data_manager: DataSourceManager,
        correction_pipeline: CorrectionPipeline,
        report_manager: ReportManager,
    ) -> None:

        self.data_manager = data_manager
        self.correction_pipeline = correction_pipeline
        self.report_manager = report_manager

    @exception_wrapper
    def run(
        self,
        xml: XML,
    ) -> str:

        atom_data = self.data_manager.load(
            xml=xml,
        )
        transformers = self.correction_pipeline.retrieve(
            data=atom_data.data,
        )
        report = self.report_manager.build(
            data=atom_data.data,
            transformers=transformers,
            dump=True,
        )

        return report
