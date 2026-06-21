import logging
import time
from collections.abc import Mapping
from functools import partial

from plugin.dto import AtomDatum
from plugin.managers.correction_manager.preview import CorrectionPreview
from plugin.managers.correction_manager.processor import CorrectionProcessor
from plugin.managers.report_manager import ReportManager
from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
)
from spectrumlab.types import Frame, R


LOGGER = logging.getLogger('plugin-absorption-correction')


class CorrectionPipeline:

    def __init__(
        self,
        report_manager: ReportManager,
        preview: CorrectionPreview,
        processor: CorrectionProcessor,
    ) -> None:

        self.report_manager = report_manager
        self.preview = preview
        self.processor = processor

    def retrieve(
        self,
        data: Mapping[str, AtomDatum],
    ) -> Mapping[str, RegressionIntensityTransformer]:
        started_at = time.perf_counter()

        LOGGER.debug(
            'Start to retrieve transformers...',
        )

        transformers = {}
        try:
            self.preview.show(
                data=data,
                update_callback=partial(self.update, transformers=transformers),
                dump_callback=partial(self.dump, data=data, transformers=transformers),
            )

        except Exception:
            LOGGER.error(
                'Time elapsed for retrieving: {elapsed:.4f}, s'.format(
                    elapsed=time.perf_counter() - started_at,
                ),
            )

        else:
            return transformers

        finally:
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(
                    'Time elapsed for retrieving: {elapsed:.4f}, s'.format(
                        elapsed=time.perf_counter() - started_at,
                    ),
                )

    def dump(
        self,
        data: Mapping[str, AtomDatum],
        transformers: Mapping[str, RegressionIntensityTransformer],
    ) -> None:

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
    ) -> tuple[tuple[R, R], Frame]:

        LOGGER.info(
            'Retrieve transformer for column %s', column_id,
        )

        result = self.processor.process(
            column_id=column_id,
            frame=frame,
            bounds=bounds,
        )

        transformers[column_id] = result.transformer

        return result.bounds, result.frame
