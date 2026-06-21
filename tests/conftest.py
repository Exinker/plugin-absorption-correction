import pytest

from spectrumlab.detectors import Detector
from spectrumlab.grids import InterpolationKind
from spectrumlab.peaks.analyte_peaks.intensity.estimators import IntegralIntensityEstimator
from spectrumlab_emulations.calibrators.concentration_calibrators import (
    AbsorbedExperimentConfig as ExperimentConfig,
)
from spectrumlab_emulations.apertures import Aperture, RectangularApertureShape
from spectrumlab_emulations.apparatus import Apparatus, VoigtApparatusShape
from spectrumlab_emulations.devices import Device
from spectrumlab_spectral_line.line import SpectralLine
from spectrumlab_spectral_line.shapes import PVoigtLineShape


@pytest.fixture(scope='module')
def config() -> ExperimentConfig:
    device = Device.GRAND2_I
    detector = Detector.BLPP4000

    return ExperimentConfig(
        device=device,
        detector=detector,
        line=SpectralLine(
            shape=PVoigtLineShape(
                width=1.7713 / device.config.dispersion,
                asymmetry=0,
                ratio=0.5843,
            ),
        ),
        apparatus=Apparatus(
            detector=detector,
            shape=VoigtApparatusShape(
                width=15.75,
                asymmetry=0.0492,
                ratio=0.4576,
            ),
        ),
        aperture=Aperture(
            detector=detector,
            shape=RectangularApertureShape(),
        ),
        position=20 / 2,
        intensity_estimator=IntegralIntensityEstimator(
            kind=InterpolationKind.LINEAR,
            interval=3,
        ),
        n_blanks=20,
        n_probes=18,
        n_parallels=5,
        concentration_blank=0,
        concentration_base=10_000,
        ref=None,
        n_numbers=20,
        n_frames=10,
        base_level=63.45,
        base_n_frames=2000,
        concentration_ratio=10 ** -0.425,
        background_level=0.00,
        scattering_ratio=0.04,
    )


@pytest.fixture(scope='module')
def column_id(
    request,
) -> str:
    return getattr(request, 'param', '0')


@pytest.fixture(scope='module')
def symbol(
    request,
) -> str:
    return getattr(request, 'param', 'Ag')


@pytest.fixture(scope='module')
def wavelength(
    request,
) -> float:
    return getattr(request, 'param', 338.289)


@pytest.fixture(scope='module')
def column_name(
    symbol: str,
    wavelength: float,
    request,
) -> str:
    return getattr(request, 'param', '{symbol} {wavelength:3.3f}'.format(
        symbol=symbol,
        wavelength=wavelength,
    ))
