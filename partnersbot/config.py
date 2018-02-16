"""
Read LICENSE file
"""
import json
from typing import Any

class Config:
    __slots__ = ('_dict', )

    def __init__(self, config_dict: dict):
        self._dict = config_dict

    def __getattr__(self, item) -> Any:
        thing = self._dict.get(item)
        if isinstance(thing, dict):
            return Config(thing)
        return thing

    def get(self, *args, **kwargs) -> Any:
        return self._dict.get(*args, **kwargs)

def config_from_file(file_path: str) -> Config:
    data = json.load(open(file_path))
    return Config(data)