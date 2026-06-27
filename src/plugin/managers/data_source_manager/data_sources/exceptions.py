from plugin.exceptions import PluginError


class DataSourceError(PluginError):
    pass


class ParseFilepathXMLError(DataSourceError):
    pass


class LoadDataXMLError(DataSourceError):
    pass


class ParseDataXMLError(DataSourceError):
    pass


class ParseMetaXMLError(ParseDataXMLError):
    pass


class ParseTableXMLError(ParseDataXMLError):
    pass
