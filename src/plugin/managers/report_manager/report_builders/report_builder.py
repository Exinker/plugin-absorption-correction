from collections.abc import Mapping
from typing import Protocol

from plugin.dto import AtomDatum
from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
)


class ReportBuilder(Protocol):

    def build(
        self,
        data: Mapping[str, AtomDatum],
        transformers: Mapping[str, RegressionIntensityTransformer],
    ) -> str:
        pass
