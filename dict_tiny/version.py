#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import importlib.metadata

__version__ = importlib.metadata.version("dict-tiny")
_metadata = importlib.metadata.metadata("dict-tiny")
name = _metadata["Name"]
DESCRIPTION = _metadata["Summary"]
