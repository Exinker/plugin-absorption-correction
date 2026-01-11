import logging
import xml.etree.ElementTree as ElementTree

from plugin.dto import AtomData, AtomFilepath
from plugin.managers.data_manager.exceptions import (
    LoadDataXMLError,
    ParseDataXMLError,
    ParseMetaXMLError,
    ParseTableXMLError,
)
from plugin.managers.data_manager.parsers.atom_meta_parser import AtomMetaParser
from plugin.managers.data_manager.parsers.atom_table_parser import AtomTableParser
from plugin.types import XML

LOGGER = logging.getLogger('plugin-absorption-correction')


class AtomDataParser:

    @classmethod
    def parse(cls, filepath: AtomFilepath) -> AtomData:

        LOGGER.debug('Load data from: %r', filepath)
        try:
            xml = load_xml(filepath)
        except LoadDataXMLError:
            raise

        LOGGER.debug('Parse data from: %r', filepath)
        try:
            data = parse_xml(filepath, xml)
        except ParseDataXMLError:
            raise

        LOGGER.debug('Data are parsed successfully!')
        return data


def load_xml(__filepath: AtomFilepath) -> XML | None:
    """Load `xml` element object from file for a given `filepath`."""

    try:
        tree = ElementTree.parse(__filepath)
    except FileNotFoundError as error:
        LOGGER.error('Parse `xml` failed: %r', error)
        raise LoadDataXMLError('File not found: {!r}!'.format(__filepath)) from error

    xml = tree.getroot()
    return xml


def parse_xml(__filepath: AtomFilepath, xml: XML) -> 'AtomData':

    try:
        meta = AtomMetaParser.parse(xml=xml)
    except Exception as error:
        LOGGER.error('Parse `meta` failed: %r', error)
        raise ParseMetaXMLError from error

    try:
        data = AtomTableParser.from_xml(xml)
    except ParseTableXMLError as error:
        LOGGER.error('Parse `data` failed: %r', error)
        raise ParseTableXMLError from error
    except Exception as error:
        LOGGER.error('Parse `data` failed with unexpected error: %r', error)
        raise ParseTableXMLError from error

    return AtomData(
        filepath=__filepath,
        meta=meta,
        data=data,
    )
