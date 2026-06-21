from base64 import b64encode
from pathlib import Path
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import numpy as np
import pandas as pd
import pytest

from spectrumlab_emulations.calibrators.concentration_calibrators import (
    ConcentrationCalibrator,
    ConcentrationCalibratorConfig,
)
from spectrumlab_emulations.emulations import (
    AbsorbedSpectrumEmulation,
    AbsorbedSpectrumEmulationConfig,
    SpectrumBaseConfig,
    SpectrumConfig,
)


@pytest.fixture(scope='module')
def emulation(
    config,
) -> AbsorbedSpectrumEmulation:
    return AbsorbedSpectrumEmulation(
        config=AbsorbedSpectrumEmulationConfig(
            device=config.device,
            detector=config.detector,

            line=config.line,
            apparatus=config.apparatus,
            aperture=config.aperture,

            spectrum=SpectrumConfig(
                n_numbers=config.n_numbers,
                n_frames=config.n_frames,
            ),
            spectrum_base=SpectrumBaseConfig(
                level=config.base_level,
                n_frames=config.base_n_frames,
            ),

            concentration_ratio=config.concentration_ratio,

            background_level=config.background_level,
            scattering_ratio=config.scattering_ratio,
        ),
    )


@pytest.fixture(scope='module')
def concentration_calibrator(
    config,
    emulation: AbsorbedSpectrumEmulation,
) -> ConcentrationCalibrator:
    concentration_calibrator = ConcentrationCalibrator(
        emulation=emulation,
        config=ConcentrationCalibratorConfig(
            intensity_estimator=config.intensity_estimator,

            concentration_blank=config.concentration_blank,
            is_clipped=False,

            n_probes=config.n_probes,
            n_parallels=config.n_parallels,

            lower_bound='LOD',
        ),
    )
    concentration_calibrator = concentration_calibrator.setup(
        position=config.position,
        concentrations=config.concentrations,
    )
    return concentration_calibrator.run(
        verbose=False,
        show=False,
        write=False,
        random_state=0,
    )


def create_test_xml(
    frame: pd.DataFrame,
    column_id: str,
    column_name: str,
) -> str:
    root = Element('root')

    titul = SubElement(root, 'titul')
    SubElement(titul, 'organization').text = 'Test Organization'
    SubElement(titul, 'device').text = 'Test Device'
    SubElement(titul, 'user').text = 'Test User'
    SubElement(titul, 'aname').text = 'Test Analysis'

    columns = SubElement(root, 'columns')
    sheet = SubElement(columns, 'sheet')

    column = SubElement(sheet, 'column')
    column.set('id', column_id)
    column.set('name', column_name)
    column.set('type', 'line')
    column.set('visible', 'yes')

    cells = SubElement(column, 'cells')
    probes = frame.index.get_level_values('probe').unique()

    for probe in probes:
        probe_data = frame.xs(probe, level='probe')
        pc = SubElement(cells, 'pc')
        pc.set('i', str(probe))
        pc.set('cm', str(probe_data['concentration'].iloc[0]))

    probes_elem = SubElement(root, 'probes')

    for probe in probes:
        probe_elem = SubElement(probes_elem, 'probe')
        probe_elem.set('id', str(probe))
        probe_elem.set('name', f'Sample{probe}')
        probe_elem.set('visible', 'yes')

        probe_data = frame.xs(probe, level='probe')
        for parallel_idx in probe_data.index:
            spe = SubElement(probe_elem, 'spe')
            spe.set('name', f'parallel{parallel_idx}')
            spe.set('disabled', 'no')

            graph = SubElement(SubElement(spe, 'graphs'), 'graph')
            graph.set('id', column_id)

            intensity = np.array([probe_data.loc[parallel_idx, 'intensity']])
            yvals = SubElement(graph, 'yvals')
            yvals.text = b64encode(intensity.astype(np.float32).tobytes()).decode('ascii')

    return minidom.parseString(
        tostring(root, encoding='unicode'),
    ).toprettyxml(indent='  ')


@pytest.fixture(scope='module')
def atom_filepath(tmp_path_factory) -> Path:
    tmpdir = tmp_path_factory.mktemp('system-data')
    return tmpdir / 'test.xml'


@pytest.fixture(scope='module')
def atom_config_xml(
    atom_filepath: Path,
    setup_atom_data,
) -> str:
    return '<input>{path}</input>'.format(path=atom_filepath)


@pytest.fixture(scope='module')
def setup_atom_data(
    column_id: str,
    column_name: str,
    concentration_calibrator: ConcentrationCalibrator,
    atom_filepath: Path,
) -> None:
    atom_filepath.write_text(
        create_test_xml(
            concentration_calibrator.data,
            column_id=column_id,
            column_name=column_name,
        ),
    )
