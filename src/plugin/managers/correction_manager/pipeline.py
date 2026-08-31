import logging
import time
from collections.abc import Mapping
from functools import partial

from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
)
from spectrumlab.types import Frame, R

from plugin.dto import AtomDatum
from plugin.managers.correction_manager.preview import CorrectionPreview
from plugin.managers.correction_manager.processor import (
    CorrectionProcessor,
    CorrectionResult,
)
from plugin.managers.report_manager import ReportManager

LOGGER = logging.getLogger('plugin-absorption-correction')


class CorrectionPipeline:

    def __init__(
        self,
        preview: CorrectionPreview,
        processor: CorrectionProcessor,
        report_manager: ReportManager,
    ) -> None:

        self.preview = preview
        self.processor = processor
        self.report_manager = report_manager

    def retrieve(
        self,
        data: Mapping[str, AtomDatum],
    ) -> Mapping[str, RegressionIntensityTransformer]:
        started_at = time.perf_counter()

        LOGGER.debug(
            'Start to retrieve correction transformers...',
        )

        transformers = {}
        try:
            self.preview.show(
                data=data,
                update_callback=partial(self.update, transformers=transformers),
                dump_callback=partial(self.dump, data=data, transformers=transformers),
            )

        except Exception as error:
            LOGGER.error(
                'Failed to show preview',
                extra=dict(
                    error=error,
                    time_elapsed=time.perf_counter() - started_at,
                ),
            )

        else:
            LOGGER.info(
                'Correction transformers retrieved successfully',
                extra=dict(
                    time_elapsed=time.perf_counter() - started_at,
                ),
            )
            return transformers

    def dump(
        self,
        data: Mapping[str, AtomDatum],
        transformers: Mapping[str, RegressionIntensityTransformer],
    ) -> None:
        LOGGER.info('Dump correction report from pipeline')

        report = self.report_manager.build(
            data=data,
            transformers=transformers,
        )
        self.report_manager.dump(
            report=report,
        )

    def update(
        self,
        column_id: str,
        frame: Frame,
        bounds: tuple[R, R] | None,
        transformers: dict[str, RegressionIntensityTransformer],
    ) -> CorrectionResult | None:

        LOGGER.info(
            'Retrieve transformer',
            extra=dict(
                column_id=column_id,
            ),
        )

        try:
            result = self.processor.process(
                column_id=column_id,
                frame=frame,
                bounds=bounds,
            )

        except Exception as error:
            LOGGER.warning(
                'Failed to retrieve transformer',
                extra=dict(
                    column_id=column_id,
                    error=error,
                ),
            )

            transformers[column_id] = None
            return None

        LOGGER.info(
            'Transformer retrieved successfully',
            extra=dict(
                column_id=column_id,
                bounds=result.bounds,
            ),
        )

        transformers[column_id] = result.transformer
        return result
