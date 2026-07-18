from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from plugin import ROOT


class PluginConfig(BaseSettings):

    filepath: Path = Field(ROOT.parents[2] / 'Temp' / 'py_table.xml', alias='FILEPATH')
    blank_name: str = Field('', alias='BLANK_NAME')
    method: Literal['amplitude', 'integral'] = Field('amplitude', alias='METHOD')
    alpha: float = Field(1e-4, ge=0, le=1, alias='ALPHA')
    n: int = Field(10, ge=1, alias='N')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


PLUGIN_CONFIG = PluginConfig()
