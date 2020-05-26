
# This contains python implementations of all the speedups
from ._speedups_fallback import *


# cython implementation of speedups. Import these if we can.
try:
    from ._cython_speedups import *
except ImportError:
    pass
