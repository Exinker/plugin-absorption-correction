import numpy as np
import pandas as pd

from plugin.managers.correction_manager import CorrectionProcessor


def test_processor_returns_bounds_transformer_and_processed_frame():
    frame = pd.DataFrame({
        'concentration': [1.0, 2.0, 3.0, 4.0],
        'intensity': [10.0, 18.0, 25.0, 31.0],
    })
    processor = CorrectionProcessor()

    result = processor.process(
        column_id='0',
        frame=frame,
        bounds=None,
    )

    assert len(result.bounds) == 2
    assert result.transformer is not None
    assert list(result.frame.columns) == [
        'concentration',
        'intensity',
        'intensity_true',
        'intensity_linearized',
    ]
    assert np.all(np.diff(result.frame['concentration']) >= 0)
