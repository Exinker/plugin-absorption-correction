from base64 import b64encode
from pathlib import Path
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import numpy as np
import pandas as pd
import pytest

from spectrumlab_emulations.calibrators.concentration_calibrators import (
    AbsorbedExperimentConfig as ExperimentConfig,
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
def config() -> ExperimentConfig:
    config = ExperimentConfig.from_ini(
        filedir=Path.cwd() / 'tests' / 'ini' / 'GRAND2_I',
        filename='Ag 338.289.ini',
    )
    return config


@pytest.fixture(scope='module')
def emulation(
    config: ExperimentConfig,
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
            # info='',
        ),
    )


@pytest.fixture(scope='module')
def concentration_calibrator(
    config: ExperimentConfig,
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
    concentration_calibrator = concentration_calibrator.run(
        verbose=False,
        show=False,
        write=False,
    )
    return concentration_calibrator


def create_test_xml(
    frame: pd.DataFrame,
    column_id: str,
    column_name: str,
    organization_name: str = 'Test Organization',
    device_name: str = 'Test Device',
    user_name: str = 'Test User',
    analysis_name: str = 'Test Analysis',
) -> str:

    root = Element('root')

    __titul = SubElement(root, 'titul')

    __organization = SubElement(__titul, 'organization')
    __organization.text = organization_name

    __device = SubElement(__titul, 'device')
    __device.text = device_name

    __user = SubElement(__titul, 'user')
    __user.text = user_name

    __aname = SubElement(__titul, 'aname')
    __aname.text = analysis_name

    __columns = SubElement(root, 'columns')
    __sheet = SubElement(__columns, 'sheet')

    __column = SubElement(__sheet, 'column')
    __column.set('id', column_id)
    __column.set('name', column_name)
    __column.set('type', 'line')
    __column.set('visible', 'yes')

    __cells = SubElement(__column, 'cells')
    probes = frame.index.get_level_values('probe').unique()

    concentrations = {}
    for probe in probes:
        probe_data = frame.xs(probe, level='probe')
        concentration = probe_data['concentration'].iloc[0]
        concentrations[probe] = concentration

        __pc = SubElement(__cells, 'pc')
        __pc.set('i', str(probe))
        __pc.set('cm', str(concentration))

    probes_elem = SubElement(root, 'probes')

    for probe in probes:
        __probe = SubElement(probes_elem, 'probe')
        __probe.set('id', str(probe))
        __probe.set('name', f'Sample{probe}')
        __probe.set('visible', 'yes')

        probe_data = frame.xs(probe, level='probe')
        parallel_indices = probe_data.index

        for parallel_idx in parallel_indices:
            __spe = SubElement(__probe, 'spe')
            __spe.set('name', f'parallel{parallel_idx}')
            __spe.set('disabled', 'no')

            __graphs = SubElement(__spe, 'graphs')
            __graph = SubElement(__graphs, 'graph')
            __graph.set('id', column_id)

            intensity = probe_data.loc[parallel_idx, 'intensity']

            y_values = np.array([intensity])
            y_values_float32 = y_values.astype(np.float32)
            y_values_b64 = b64encode(y_values_float32.tobytes()).decode('ascii')
            __yvals = SubElement(__graph, 'yvals')
            __yvals.text = y_values_b64

    return minidom.parseString(
        tostring(root, encoding='unicode'),
    ).toprettyxml(indent='  ')


@pytest.fixture(scope='module')
def filepath(tmp_path_factory) -> Path:
    tmpdir = tmp_path_factory.mktemp('data')

    return tmpdir / 'test.xml'


@pytest.fixture(scope='module', autouse=True)
def setup(
    column_id: str,
    column_name: str,
    concentration_calibrator: ConcentrationCalibrator,
    filepath: Path,
) -> Path:

    xml = create_test_xml(
        concentration_calibrator.data,
        column_id=column_id,
        column_name=column_name,
    )

    with open(filepath, 'w') as file:
        file.write(xml)
