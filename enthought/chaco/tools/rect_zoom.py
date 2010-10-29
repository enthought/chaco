""" Defines the RectZoomTool class.
"""
import warnings
warnings.warn("RectZoomTool has been deprecated, use ZoomTool", DeprecationWarning)

from simple_zoom import SimpleZoom

class RectZoomTool(SimpleZoom):
    """
    Allows the user to drag a zoom box around a region of the plot.
    
    This is a subclass of SimpleZoom, with different default values for some
    traits.
    """

    # Selects a box in two dimensions (overrides SimpleZoom).
    tool_mode = "box"

    # The tool is always on; left-clicking initiates a zoom (overrides 
    # SimpleZoom).
    always_on = True

