
# This is a duplicate of the enable.DragTool class and will be
# removed in future versions.  Please import DragTool directly
# from enable.

import warnings
warnings.warn("enthought.chaco.tools.DragTool has been removed."
              "Use enthought.enable.tools.DragTool instead.", DeprecationWarning)

from enthought.enable.tools.drag_tool import DragTool

