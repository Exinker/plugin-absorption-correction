import logging
from base64 import b64decode
from collections import defaultdict
from collections.abc import Mapping

import numpy as np
import pandas as pd

from plugin.config import PLUGIN_CONFIG
from plugin.dto import AtomDatum
from plugin.managers.data_manager.exceptions import ParseTableXMLError
from plugin.types import XML
from spectrumlab.types import Array

LOGGER = logging.getLogger('plugin-absorption-correction')


class AtomTableParser:

    @classmethod
    def from_xml(cls, __xml: XML) -> Mapping[str, AtomDatum]:

        # lines
        line = []
        for __column in __xml.find('columns').findall('sheet/column'):
            if (__column.attrib.get('visible') == 'no') or (__column.attrib.get('type') != 'line'):
                continue

            column_id = __column.attrib['id']
            nickname = __column.attrib['name']
            line.append(dict(
                line_id=column_id,
                nickname=nickname,
            ))
        line = pd.DataFrame(line).set_index('line_id')

        # concentrations
        concentrations = defaultdict(list)
        for __column in __xml.find('columns').findall('sheet/column'):
            column_id = __column.attrib['id']
            if column_id in line.index:

                for __probe in __column.findall('cells/pc'):
                    concentrations[column_id].append(dict(
                        probe_id=__probe.attrib['i'],
                        value=float(__probe.attrib.get('cm', 'nan')),
                    ))
        concentrations = {
            key: pd.DataFrame(concentrations[key]).set_index('probe_id')
            for key in concentrations.keys()
        }

        # datum
        datum = defaultdict(list)
        for __probe in __xml.find('probes').findall('probe'):
            if __probe.attrib.get('visible', 'no') == 'no':
                continue

            probe_id = __probe.attrib['id']
            probe_name = __probe.attrib['name']

            for __spe in __probe.findall('spe'):
                if __spe.attrib.get('disabled', 'no') == 'yes':
                    continue

                parallel_name = __spe.attrib['name']

                for __graph in __spe.findall('graphs/graph'):
                    column_id = __graph.attrib['id']

                    if column_id in line.index:

                        try:
                            value = parse_intensity(__graph)
                            if __graph.find('bad'):
                                mask = parse_mask(__graph)
                                value = np.where(~mask, value, np.nan)

                        except Exception as error:
                            LOGGER.error(
                                'Parse column %d failed', column_id,
                            )
                            raise ParseTableXMLError from error

                        datum[column_id].append(dict(
                            probe_name=probe_name,
                            parallel_name=parallel_name,
                            concentration=concentrations[column_id].loc[probe_id, 'value'],
                            intensity=np.nanmax(value),
                            value=value,
                        ))

        # bounds
        bounds = {}

        __plugin = __xml.find('plugin-absorption-correction')
        if __plugin:
            for __column in __plugin.findall('column'):
                column_id = __column.attrib['id']

                __bounds = __column.find('bounds')
                bounds[column_id] = (float(__bounds.attrib['lb']), float(__bounds.attrib['ub']))

        # polynom
        polynom = defaultdict(list)

        __plugin = __xml.find('plugin-absorption-correction')
        if __plugin:
            for __column in __plugin.findall('column'):
                column_id = __column.attrib['id']

                __polynom = __column.find('polynom')
                for __point in __polynom.findall('point'):
                    polynom[column_id].append((float(__point.attrib['x']), float(__point.attrib['y'])))

        # data
        data = {}
        for column_id in datum.keys():
            nickname = line.loc[column_id, 'nickname']

            frame = pd.DataFrame(datum[column_id]).set_index(['probe_name', 'parallel_name'])
            if PLUGIN_CONFIG.black_name in frame.index:
                blank = frame.loc[PLUGIN_CONFIG.black_name, 'intensity'].mean().item()

                frame['intensity'] -= blank
                frame['value'] -= blank

            data[column_id] = AtomDatum(
                column_id=column_id,
                nickname=nickname,
                frame=frame,
                bounds=bounds.get(column_id),
                polynom=polynom.get(column_id),
            )
        return data


def numpy_array_from_b64(buffer: str, dtype: type) -> Array[float]:
    return np.frombuffer(b64decode(buffer.strip()), dtype=dtype)


def parse_intensity(__graph: XML) -> Array[float]:
    xpath = 'yvals'

    try:
        return numpy_array_from_b64(__graph.find(xpath).text, dtype=np.float32)

    except Exception:
        LOGGER.error("Parse `intensity` failed. Check xpath: %r", xpath)
        raise


def parse_mask(__graph: XML) -> Array[bool]:
    xpath = 'yvals'

    try:
        mask = np.full(int(__graph.find(xpath).get('value_array_size')), False)
        mask[numpy_array_from_b64(__graph.find('bad').text, dtype=np.int32)] = True
        return mask

    except Exception:
        LOGGER.error("Parse `intensity` failed. Check xpath: %r", xpath)
        raise
