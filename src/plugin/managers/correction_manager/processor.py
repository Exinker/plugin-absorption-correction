import logging
from dataclasses import dataclass

from plugin.managers.correction_manager.core import process_data
from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
    estimate_bounds,
    process_frame,
)
from spectrumlab.types import Frame, R


LOGGER = logging.getLogger('plugin-absorption-correction')


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
        LOGGER.info(
            'Start correction processing: column=%s, rows=%d, bounds=%r',
            column_id,
            len(frame),
            bounds,
        )

        data = process_frame(frame)
        if bounds is None:
            bounds = estimate_bounds(data)
            LOGGER.info(
                'Correction bounds estimated: column=%s, bounds=%r',
                column_id,
                bounds,
            )
        else:
            LOGGER.info(
                'Use saved correction bounds: column=%s, bounds=%r',
                column_id,
                bounds,
            )

        transformer = RegressionIntensityTransformer.create(
            data=data,
            bounds=bounds,
        )
        processed_data = process_data(
            frame,
            transformer=transformer,
        )

        LOGGER.info(
            'Correction processing finished: column=%s, rows=%d',
            column_id,
            len(processed_data),
        )

        return CorrectionResult(
            bounds=bounds,
            transformer=transformer,
            frame=processed_data,
        )
