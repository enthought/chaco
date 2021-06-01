import warnings

from chaco.overlays.api import ErrorLayer, StatusLayer, WarningLayer

warnings.warn(
    "chaco/layers has been moved to sit in chaco/overlays/layers. Importing "
    "from chaco.layers.api is deprecated, please import from "
    "chaco.overlays.api going forward as chaco/layers will be removed in a "
    "future release.",
    DeprecationWarning,
    stacklevel=2,
)
