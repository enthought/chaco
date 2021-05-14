""" Defines the RectZoomTool class.
"""
from .selecting_zoom_tool import SelectingZoomTool


class RectZoomTool(SelectingZoomTool):
    """
    Allows the user to drag a zoom box around a region of the plot.

    This is a subclass of SelectingZoomTool, with different default values for
    some traits.
    """

    #: Selects a box in two dimensions (overrides SelectingZoomTool).
    tool_mode = "box"

    #: The tool is always on; left-clicking initiates a zoom (overrides
    #: SelectingZoomTool).
    always_on = True
