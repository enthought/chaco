#  Copyright (c) 2005-2014 by Enthought, Inc.
#  All rights reserved.
""" Two-dimensional plotting application toolkit.
    Part of the Chaco project of the Enthought Tool Suite.
"""
try:
    from chaco._version import full_version as __version__  # noqa
except ImportError:
    __version__ = "not-built"

__requires__ = ["traits", "traitsui", "pyface", "numpy", "enable"]
