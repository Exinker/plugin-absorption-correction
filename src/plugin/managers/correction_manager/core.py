import pandas as pd

from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
)
from spectrumlab.types import Frame


def process_data(
    __data: Frame,
    transformer: RegressionIntensityTransformer,
) -> Frame:

    data = pd.DataFrame(
        {
            'concentration': __data['concentration'],
            'intensity': __data['intensity'],
            'intensity_true': transformer.estimate_intensity(__data['concentration']),
            'intensity_linearized': transformer.apply(__data['intensity']),
        },
        index=__data.index,
    )

    return data.sort_values(by='concentration')
