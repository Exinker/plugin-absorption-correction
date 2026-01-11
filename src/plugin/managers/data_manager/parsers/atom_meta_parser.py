import logging

from plugin.dto import AtomMeta
from plugin.types import XML

LOGGER = logging.getLogger('plugin-absorption-correction')


class AtomMetaParser:

    @classmethod
    def parse(cls, xml: XML) -> AtomMeta:
        titul = xml.find('titul')

        return AtomMeta(
            organization_name=titul.find('organization').text,
            device_name=titul.find('device').text,
            user_name=titul.find('user').text,
            analysis_name=titul.find('aname').text,
        )
