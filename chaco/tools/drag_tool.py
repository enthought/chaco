# This is a duplicate of the enable.DragTool class and will be
# removed in future versions.  Please import DragTool directly
# from enable.

import warnings

warnings.warn(
    "chaco.tools.DragTool has been removed."
    "Use enable.tools.DragTool instead.",
    DeprecationWarning,
)

from enable.tools.api import DragTool
