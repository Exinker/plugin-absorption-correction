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
        [
            {
                'probe': i,
                'parallel': j,
                'concentration': __data.loc[(i, j), 'concentration'],
                'intensity': __data.loc[(i, j), 'intensity'],
                'intensity_true': transformer.estimate_intensity(__data.loc[(i, j), 'concentration']),
                'intensity_linearized': transformer(__data.loc[(i, j), 'intensity']),
            }
            for i, j in __data.drop(index='blank', errors='ignore').index
        ],
        columns=['probe', 'parallel', 'concentration', 'intensity', 'intensity_true', 'intensity_linearized'],
    ).set_index(['probe', 'parallel'])

    return data.sort_values(by='concentration')
