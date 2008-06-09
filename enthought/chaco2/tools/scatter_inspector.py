""" Defines the ScatterInspector tool class.
"""

# Enthought library imports
from enthought.enable2.api import BaseTool
from enthought.traits.api import Any, Bool, Enum, Float, Str

# Chaco imports
from enthought.chaco2.api import ScatterPlot


class ScatterInspector(BaseTool):
    """ A tool for inspecting scatter plots. 
    
    It writes the index of the point under the cursor to the metadata of the 
    index and value data sources, and allows clicking to select the point. 
    Other components can listen for metadata updates on the data sources.
    
    By default, it writes the index of the point under the cursor to the "hover"
    key in metadata, and the index of a clicked point to "selection".
    """

    # The threshold, in pixels, around the cursor location to search for points.
    threshold = Float(5.0)

    # Can the user left-click to select a point?
    enable_select = Bool(True)
    
    # This tool is not visible (overrides BaseTool).
    visible = False

    # This tool does not have a visual reprentation (overrides BaseTool).
    draw_mode = "none"

    def normal_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'normal' state.
        
        If the cursor is within **threshold** of a data point, the method 
        writes the index to the plot's data sources' "hover" metadata.
        """
        plot = self.component
        index = plot.map_index((event.x, event.y), threshold=self.threshold)
        if index:
            plot.index.metadata["hover"] = index
            plot.value.metadata["hover"] = index
        else:
            plot.index.metadata.pop("hover", None)
            plot.value.metadata.pop("hover", None)
        event.handled = True
        return
    
    def normal_left_down(self, event):
        """ Handles the left mouse button being pressed when the tool is in the
        'normal' state.
        
        If selecting is enabled and the cursor is within **threshold** of a
        data point, the method writes the index to the plot's data sources'
        "selection" metadata.
        """
        if self.enable_select:
            plot = self.component
            index = plot.map_index((event.x, event.y), threshold=self.threshold)
            if index:
                plot.index.metadata["selection"] = index
                plot.value.metadata["selection"] = index
            else:
                plot.index.metadata.pop("selection", None)
                plot.value.metadata.pop("selection", None)
            event.handled = True
        return


# EOF
