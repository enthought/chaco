""" Defines the RectZoomTool class.
"""
from .zoom_tool import ZoomTool


class RectZoomTool(ZoomTool):
    """
    Allows the user to drag a zoom box around a region of the plot.

    This is a subclass of ZoomTool, with different default values for some
    traits.
    """

    #: Selects a box in two dimensions (overrides ZoomTool).
    tool_mode = "box"

    #: The tool is always on; left-clicking initiates a zoom (overrides
    #: ZoomTool).
    always_on = True
