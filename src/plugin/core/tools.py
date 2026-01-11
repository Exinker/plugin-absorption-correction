from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from spectrumlab.types import C, Frame


DATASHEET = {
    'Ag': {
        -2: 52400,
        -1: 26200,
        0: 10000,
    },
    'otherwise': {
        0: 50000,
    },
}


def load_dat(
    label: str,
) -> Frame:

    def calculate_concentration(
        label: str,
        i: int | Literal['blank'],
    ) -> C:
        if i == 'blank':
            return 0

        i = int(i)

        element, *_ = label.split(' ')

        if element == 'Ag':
            if i < 0:
                return DATASHEET['Ag'][i]
            return DATASHEET['Ag'][0] * (1/(2**i))

        assert i >= 0
        return DATASHEET['otherwise'][0] * (1/(2**i))

    data = []
    for filepath in (Path.cwd() / 'data' / label).glob('*/*.txt'):
        i = filepath.parent.stem
        j = filepath.stem

        intensity = pd.read_csv(
            filepath,
            sep='\t',
            decimal=',',
            names=['time', 'intensity'],
        ).set_index('time')

        data.append({
            'probe': i,
            'parallel': j,
            'concentration': calculate_concentration(
                label=label,
                i=i,
            ),
            'intensity': np.array(intensity['intensity']),
        })

    data = pd.DataFrame(
        data,
        columns=['probe', 'parallel', 'intensity', 'concentration'],
    ).set_index(['probe', 'parallel'])

    return data
