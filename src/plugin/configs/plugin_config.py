from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from plugin import ROOT


class PluginConfig(BaseSettings):

    filepath: Path = Field(ROOT.parents[1] / 'Temp' / 'py_table.xml', alias='FILEPATH')
    blank_name: str = Field('', alias='BLANK_NAME')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


PLUGIN_CONFIG = PluginConfig()
