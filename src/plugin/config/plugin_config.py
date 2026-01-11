from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_MAX_WORKERS = 1


class LoggingLevel(Enum):

    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class PluginConfig(BaseSettings):

    logging_level: LoggingLevel = Field(LoggingLevel.INFO, alias='LOGGING_LEVEL')
    black_name: str = Field('', alias='BLACK_NAME')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


PLUGIN_CONFIG = PluginConfig()
