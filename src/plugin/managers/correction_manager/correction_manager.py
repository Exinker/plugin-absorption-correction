import logging
import time
from collections.abc import Mapping
from functools import partial

from plugin.config import PluginConfig
from plugin.dto import AtomDatum
from plugin.managers.correction_manager.core import process_data
from plugin.managers.report_manager import ReportManager
from plugin.presentation import retrieve_transformer
from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
    estimate_bounds,
    process_frame,
)
from spectrumlab.types import Frame, R


LOGGER = logging.getLogger('plugin-absorption-correction')


class CorrectionManager:

    def __init__(
        self,
        plugin_config: PluginConfig,
        report_manager: ReportManager,
    ) -> None:

        self.plugin_config = plugin_config
        self.report_manager = report_manager

        self.transformers = None

    def retrieve(
        self,
        data: Mapping[str, AtomDatum],
    ) -> Mapping[str, RegressionIntensityTransformer]:
        started_at = time.perf_counter()

        LOGGER.debug(
            'Start to retrieve transformers...',
        )

        self.transformers = {}
        try:
            retrieve_transformer(
                data=data,
                update_callback=self.update,
                dump_callback=partial(self.dump, data=data),
            )

        except Exception as error:
            LOGGER.error(
                'Time elapsed for retrieving: {elapsed:.4f}, s'.format(
                    elapsed=time.perf_counter() - started_at,
                ),
            )

        else:
            return self.transformers

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
    ) -> None:
        assert self.transformers is not None

        report = self.report_manager.build(
            data=data,
            transformers=self.transformers,
        )
        self.report_manager.dump(
            report=report,
        )

    def update(
        self,
        column_id: str,
        frame: Frame,
        bounds: tuple[R, R] | None,
    ) -> tuple[tuple[R, R], Frame]:
        assert self.transformers is not None

        data = process_frame(frame)
        bounds = bounds or estimate_bounds(data)

        self.transformers[column_id] = RegressionIntensityTransformer.create(
            data=data,
            bounds=bounds,
        )

        processed_data = process_data(
            frame,
            transformer=self.transformers[column_id],
        )
        return bounds, processed_data
