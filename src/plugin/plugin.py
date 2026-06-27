import logging
import time
from typing import Self

from plugin.exceptions import exception_wrapper
from plugin.managers.correction_manager import CorrectionPipeline, CorrectionPreview, CorrectionProcessor
from plugin.managers.data_source_manager import DataSourceManager
from plugin.managers.data_source_manager.data_sources import XMLDataSource
from plugin.managers.report_manager import ReportManager, XMLReportBuilder

LOGGER = logging.getLogger('plugin-absorption-correction')


class Plugin:

    @classmethod
    def create(
        cls,
        data_source: XMLDataSource,
        preview: CorrectionPreview,
    ) -> Self:

        data_source_manager = DataSourceManager(
            data_source=data_source,
        )
        report_manager = ReportManager(
            report_builder=XMLReportBuilder(),
        )
        correction_pipeline = CorrectionPipeline(
            preview=preview,
            processor=CorrectionProcessor(),
            report_manager=report_manager,
        )

        return Plugin(
            data_source_manager=data_source_manager,
            correction_pipeline=correction_pipeline,
            report_manager=report_manager,
        )

    def __init__(
        self,
        data_source_manager: DataSourceManager,
        correction_pipeline: CorrectionPipeline,
        report_manager: ReportManager,
    ) -> None:

        self.data_source_manager = data_source_manager
        self.correction_pipeline = correction_pipeline
        self.report_manager = report_manager

    @exception_wrapper
    def run(self) -> str:
        started_at = time.perf_counter()

        LOGGER.info('Start absorption correction plugin')

        atom_data = self.data_source_manager.load()
        LOGGER.info(
            'Atom data loaded',
            extra=dict(
                columns=len(atom_data.data),
            ),
        )

        transformers = self.correction_pipeline.retrieve(
            data=atom_data.data,
        )
        LOGGER.info(
            'Correction transformers retrieved',
        )

        report = self.report_manager.build(
            data=atom_data.data,
            transformers=transformers,
            dump=True,
        )
        LOGGER.info(
            'Absorption correction finished successfully',
            extra=dict(
                time_elapsed=time.perf_counter() - started_at,
            ),
        )

        return report
