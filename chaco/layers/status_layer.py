import warnings

from chaco.overlays.layers.status_layer import (  # noqa: F401
    ErrorLayer, StatusLayer, WarningLayer
)

warnings.warn(
    "chaco/layers has been moved to sit in chaco/overlays/layers. Importing "
    "from this module is deprecated, please import from "
    "chaco.overlays.api going forward as chaco/layers will be removed in a "
    "future release.",
    DeprecationWarning,
    stacklevel=2,
)
