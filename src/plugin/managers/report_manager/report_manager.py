import logging
import time
from collections.abc import Mapping

from plugin.config import PluginConfig
from plugin.dto import AtomDatum
from plugin.managers.report_manager.report_builders import ReportBuilder, XMLReportBuilder
from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
)


LOGGER = logging.getLogger('plugin-absorption-correction')


class ReportManager:

    def __init__(
        self,
        plugin_config: PluginConfig,
        report_builder: ReportBuilder,
    ) -> None:

        self.plugin_config = plugin_config
        self.report_builder = report_builder

    def build(
        self,
        data: Mapping[str, AtomDatum],
        transformers: Mapping[str, RegressionIntensityTransformer],
        dump: bool = False,
    ) -> str:
        started_at = time.perf_counter()

        LOGGER.info(
            'Start report building: report_builder=%s, columns=%d, dump=%s',
            self.report_builder.__class__.__name__,
            len(data),
            dump,
        )

        report = self.report_builder.build(
            data=data,
            transformers=transformers,
        )

        if dump:
            self.dump(
                report=report,
            )

        LOGGER.info(
            'Report built: size=%d, elapsed=%.4f, s',
            len(report),
            time.perf_counter() - started_at,
        )

        return report

    @classmethod
    def default(cls) -> str:
        LOGGER.info('Build default error report.')
        return XMLReportBuilder.default()

    def dump(
        self,
        report: str,
        filename: str = 'results',
    ) -> None:

        filepath = f'{filename}.xml'
        LOGGER.info(
            'Dump report: filepath=%r, size=%d',
            filepath,
            len(report),
        )
        with open(filepath, 'w') as file:
            file.write(report)
