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
            'Start correction processing',
            extra=dict(
                column_id=column_id,
                bounds=bounds,
            ),
        )

        data = process_frame(frame)
        if bounds is None:
            bounds = estimate_bounds(data)
            LOGGER.info(
                'Correction bounds estimated',
                extra=dict(
                    column_id=column_id,
                    bounds=bounds,
                ),
            )
        else:
            LOGGER.info(
                'Use exists correction bounds',
                extra=dict(
                    column_id=column_id,
                    bounds=bounds,
                ),
            )

        transformer = RegressionIntensityTransformer.create(
            intensity=data['intensity'].to_numpy(),
            concentration=data['concentration'].to_numpy(),
            bounds=bounds,
        )
        processed_data = process_data(
            frame,
            transformer=transformer,
        )

        LOGGER.info(
            'Correction processing finished successfully',
            extra=dict(
                column_id=column_id,
            ),
        )

        return CorrectionResult(
            bounds=bounds,
            transformer=transformer,
            frame=processed_data,
        )
