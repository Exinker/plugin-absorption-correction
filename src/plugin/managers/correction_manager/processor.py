import logging
from dataclasses import dataclass

from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    AmplitudeKernel,
    IntegralKernel,
    RegressionIntensityTransformer,
    estimate_bounds,
    process_frame,
)
from spectrumlab.types import Frame, R

from plugin.config import PLUGIN_CONFIG
from plugin.managers.correction_manager.core import process_data


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

        match PLUGIN_CONFIG.method:

            case 'amplitude':
                transformer = RegressionIntensityTransformer(
                    kernel=AmplitudeKernel(
                        intensity=data['intensity'].to_numpy(),
                        concentration=data['concentration'].to_numpy(),
                        bounds=bounds,
                    ),
                )

            case 'integral':
                transformer = RegressionIntensityTransformer(
                    kernel=IntegralKernel(
                        intensity=data['intensity'].to_numpy(),
                        concentration=data['concentration'].to_numpy(),
                        value=frame.loc[data.index]['value'],
                        bounds=bounds,
                        alpha=PLUGIN_CONFIG.alpha,
                        n=PLUGIN_CONFIG.n,
                    ),
                )

            case _:
                NotImplementedError(f'Method {PLUGIN_CONFIG.method} not supported yet!')

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
