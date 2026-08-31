from collections.abc import Mapping
from typing import Protocol

from spectrumlab.peaks.analyte_peaks.intensity.transformers import RegressionIntensityTransformer

from plugin.dto import AtomDatum


class ReportBuilder(Protocol):

    def build(
        self,
        data: Mapping[str, AtomDatum],
        transformers: Mapping[str, RegressionIntensityTransformer],
    ) -> str:
        pass
