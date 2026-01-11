import random

import pytest

from spectrumlab.elements import PeriodicTable


PERIODIC_TABLE = PeriodicTable()


@pytest.fixture(scope='module')
def column_id(
    faker,
    request,
) -> str:
    return getattr(request, 'param', str(faker.pyint(min_value=0, max_value=100)))


@pytest.fixture(scope='module')
def symbol(
    request,
) -> str:
    return getattr(request, 'param', random.choice(PERIODIC_TABLE.database['symbol']))


@pytest.fixture(scope='module')
def wavelength(
    faker,
    request,
) -> float:
    return getattr(request, 'param', faker.pyfloat(min_value=100, max_value=1000))


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
