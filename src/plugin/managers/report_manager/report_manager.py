from collections.abc import Mapping

from plugin.config import PluginConfig
from plugin.dto import AtomDatum
from plugin.managers.report_manager.report_builders import ReportBuilder, XMLReportBuilder
from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
)


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

        report = self.report_builder.build(
            data=data,
            transformers=transformers,
        )

        if dump:
            self.dump(
                report=report,
            )

        return report

    @classmethod
    def default(cls) -> str:
        return XMLReportBuilder.default()

    def dump(
        self,
        report: str,
        filename: str = 'results',
    ) -> None:

        filepath = f'{filename}.xml'
        with open(filepath, 'w') as file:
            file.write(report)
