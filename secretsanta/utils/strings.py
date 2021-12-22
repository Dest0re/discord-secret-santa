import json
from collections import namedtuple

from .environmentvariables import EnvironmentVariables

_env = EnvironmentVariables('STRINGS_JSON_PATH')

with open(_env.STRINGS_JSON_PATH, encoding="utf-8") as f:
    strings = json.load(f)

TextStrings = namedtuple('TextStrings', strings.keys())

text_strings = TextStrings(**strings)
