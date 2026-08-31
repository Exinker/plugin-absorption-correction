import logging
import math
import xml.etree.ElementTree as ElementTree
from collections.abc import Mapping, Sequence
from xml.dom import minidom

from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
)

from plugin.dto import AtomDatum


LOGGER = logging.getLogger('plugin-absorption-correction')


class XMLReportBuilder:

    def build(
        self,
        data: Mapping[str, AtomDatum],
        transformers: Mapping[str, RegressionIntensityTransformer],
    ) -> str:
        LOGGER.info(
            'Start report building with XML',
            extra=dict(
                columns=len(data),
            ),
        )

        results = []
        for column_id, datum in data.items():
            LOGGER.debug(
                'Build XML report column',
                extra=dict(
                    column_id=column_id,
                    nickname=datum.nickname,
                ),
            )

            if transformers[column_id] is not None:
                results.append(dict(
                    id=column_id,
                    nickname=datum.nickname,
                    bounds=self._build_bounds(
                        transformer=transformers[column_id],
                    ),
                    polynom=self._build_polynom(
                        datum=datum,
                        transformer=transformers[column_id],
                    ),
                ))

        report = wrap(results)
        LOGGER.info(
            'XML report built successfully',
            extra=dict(
                results=len(results),
            ),
        )
        return report

    def _build_bounds(
        self,
        transformer: RegressionIntensityTransformer,
    ) -> Mapping[str, str]:
        lb, ub = transformer.kernel.bounds

        bounds = {
            'lb': str(lb),
            'ub': str(ub),
        }
        return bounds

    def _build_polynom(
        self,
        datum: AtomDatum,
        transformer: RegressionIntensityTransformer,
    ) -> Sequence[Mapping[str, str]]:

        frame = datum.frame.copy()
        frame = frame.dropna(subset=['concentration'])
        frame = frame.groupby(level=0, sort=False).mean(numeric_only=True)
        frame['intensity_hat'] = transformer.predict(frame['intensity'])

        data = []
        for index in frame.index:
            x = float(frame.loc[index, 'intensity'].item())
            y = float(frame.loc[index, 'intensity_hat'].item())
            if not (math.isfinite(x) and math.isfinite(y)):
                continue

            data.append({
                'x': str(x),
                'y': str(y),
            })
        return tuple(data)

    @classmethod
    def default(cls) -> str:
        LOGGER.info('Build default XML report')

        root = ElementTree.Element('columns')

        ElementTree.SubElement(root, 'message', text='Absorption correction failed!')
        ElementTree.SubElement(root, 'message', text='Open `${ATOM_PATH}/Data/.log` to more information')

        reparsed = minidom.parseString(
            string=ElementTree.tostring(root, encoding='utf-8'),
        )

        xml = reparsed.toprettyxml(indent='', encoding='utf-8').decode('utf-8')
        return xml


def wrap(__data) -> str:
    root = ElementTree.Element('columns')

    for datum in __data:
        column = ElementTree.SubElement(root, 'column', id=datum['id'], nickname=datum['nickname'])

        ElementTree.SubElement(column, 'bounds', **datum['bounds'])

        polynom = ElementTree.SubElement(column, 'polynom')
        for point in datum['polynom']:
            ElementTree.SubElement(polynom, 'point', **point)

    reparsed = minidom.parseString(
        string=ElementTree.tostring(root, encoding='utf-8'),
    )

    xml = reparsed.toprettyxml(indent='', encoding='utf-8').decode('utf-8')
    return xml
