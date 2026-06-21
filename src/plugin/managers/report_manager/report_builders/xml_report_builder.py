import xml.etree.ElementTree as ElementTree
from collections.abc import Mapping, Sequence
from xml.dom import minidom

from plugin.dto import AtomDatum
from spectrumlab.peaks.analyte_peaks.intensity.transformers import (
    RegressionIntensityTransformer,
)


class XMLReportBuilder:

    def build(
        self,
        data: Mapping[str, AtomDatum],
        transformers: Mapping[str, RegressionIntensityTransformer],
    ) -> str:

        results = []
        for column_id, datum in data.items():

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

        return wrap(results)

    def _build_bounds(
        self,
        transformer: RegressionIntensityTransformer,
    ) -> Mapping[str, str]:
        lb, ub = transformer.bounds

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
        frame = frame.groupby(level=0, sort=False).mean()
        frame['intensity_hat'] = transformer.apply(frame['intensity'])

        data = []
        for index in frame.index:
            data.append({
                'x': str(frame.loc[index, 'intensity'].item()),
                'y': str(frame.loc[index, 'intensity_hat'].item()),
            })
        return tuple(data)

    @classmethod
    def default(cls) -> str:
        root = ElementTree.Element('columns')

        ElementTree.SubElement(root, 'message', text='Absorption correction failed!')
        ElementTree.SubElement(root, 'message', text='Open `${ATOM_PATH}/Data/.log` to more information.')

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
