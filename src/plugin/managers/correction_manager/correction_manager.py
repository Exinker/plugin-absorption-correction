import logging
import time
from collections.abc import Mapping

from plugin.config import PluginConfig
from plugin.dto import AtomDatum
from plugin.managers.correction_manager.core import process_data
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
    ) -> None:

        self.plugin_config = plugin_config

        self.transformer = {}

    def retrieve(
        self,
        data: Mapping[str, AtomDatum],
    ) -> Mapping[str, RegressionIntensityTransformer]:
        started_at = time.perf_counter()

        LOGGER.debug(
            'Start to restoring transformer...',
        )
        try:
            retrieve_transformer(
                data=data,
                callback=self.update,
            )
        except Exception as error:
            LOGGER.error(
                'Time elapsed for restoring: {elapsed:.4f}, s'.format(
                    elapsed=time.perf_counter() - started_at,
                ),
            )
        else:
            return self.transformer
        finally:
            if LOGGER.isEnabledFor(logging.INFO):
                LOGGER.info(
                    'Time elapsed for restoring: {elapsed:.4f}, s'.format(
                        elapsed=time.perf_counter() - started_at,
                    ),
                )

    def update(
        self,
        column_id: str,
        frame: Frame,
        bounds: tuple[R, R] | None,
    ) -> tuple[tuple[R, R], Frame]:
        data = process_frame(frame)
        bounds = bounds or estimate_bounds(data)

        self.transformer[column_id] = RegressionIntensityTransformer.create(
            data=data,
            bounds=bounds,
        )

        processed_data = process_data(
            frame,
            transformer=self.transformer[column_id],
        )
        return bounds, processed_data
