from dataclasses import dataclass

from plugin.managers.correction_manager.core import process_data
from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
    estimate_bounds,
    process_frame,
)
from spectrumlab.types import Frame, R


@dataclass(frozen=True)
class CorrectionResult:
    bounds: tuple[R, R]
    transformer: RegressionIntensityTransformer
    frame: Frame


class CorrectionProcessor:

    def process(
        self,
        column_id: str,
        frame: Frame,
        bounds: tuple[R, R] | None,
    ) -> CorrectionResult:

        data = process_frame(frame)
        bounds = bounds or estimate_bounds(data)

        transformer = RegressionIntensityTransformer.create(
            data=data,
            bounds=bounds,
        )
        processed_data = process_data(
            frame,
            transformer=transformer,
        )

        return CorrectionResult(
            bounds=bounds,
            transformer=transformer,
            frame=processed_data,
        )
