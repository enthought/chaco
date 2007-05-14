
from simple_zoom import SimpleZoom


class RectZoomTool(SimpleZoom):
    """
    Allows the user to drag a zoom box around a region of the plot.
    
    Just a SimpleZoom tool with different default values for some traits.
    """
    
    tool_mode = "box"

    always_on = True
    