import logging
import time
from collections.abc import Mapping

from plugin.dto import AtomDatum
from plugin.managers.report_manager.report_builders import ReportBuilder, XMLReportBuilder
from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
)


LOGGER = logging.getLogger('plugin-absorption-correction')


class ReportManager:

    def __init__(
        self,
        report_builder: ReportBuilder,
    ) -> None:

        self.report_builder = report_builder

    def build(
        self,
        data: Mapping[str, AtomDatum],
        transformers: Mapping[str, RegressionIntensityTransformer],
        dump: bool = False,
    ) -> str:
        started_at = time.perf_counter()

        LOGGER.info(
            'Start report building with %s',
            self.report_builder.__class__.__name__,
            extra=dict(
                dump=dump,
            ),
        )

        report = self.report_builder.build(
            data=data,
            transformers=transformers,
        )

        if dump:
            self.dump(
                report=report,
            )

        LOGGER.info('Report built successfully')

        return report

    @classmethod
    def default(cls) -> str:
        LOGGER.info('Build default error report')
        return XMLReportBuilder.default()

    def dump(
        self,
        report: str,
        filename: str = 'results',
    ) -> None:

        filepath = f'{filename}.xml'
        LOGGER.info(
            'Dump report',
            extra=dict(
                filepath=filepath,
            ),
        )
        with open(filepath, 'w') as file:
            file.write(report)
