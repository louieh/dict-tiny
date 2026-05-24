#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import tomllib
from pathlib import Path

_pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
_data = tomllib.loads(_pyproject.read_text())

name = _data["project"]["name"]
__version__ = _data["project"]["version"]
DESCRIPTION = _data["project"]["description"]
