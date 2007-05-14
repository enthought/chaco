
# Major library imports
from numpy import array, take, transpose

# Enthought library imports
from enthought.enable2.api import ColorTrait
from enthought.traits.api import Any, Enum, false, Float, Str, true

# Chaco imports
from enthought.chaco2.api import BaseTool, ScatterPlot


class ScatterInspector(BaseTool):
    """
    Tool for inspecting scatter plots.  Writes the index of the point under the
    cursor to the metadata of the index and value datasources, and allows clicking
    to select the point.  Other components can listen for metadata updates on the
    datasources.
    
    By default, writes the index of the point under the cursor to the "hover"
    key in metadata, and the indices of the clicked point to "selection".
    """
    
    visible = False
    draw_mode = "none"

    # The threshold, in pixels, around the cursor location to search for points
    threshold = Float(5.0)

    # Should the user be able to left-click to select a point?
    enable_select = true

    def normal_mouse_move(self, event):
        plot = self.component
        index = plot.map_index((event.x, event.y), threshold=self.threshold)
        if index:
            plot.index.metadata["hover"] = index
            plot.value.metadata["hover"] = index
        return
    
    def normal_left_down(self, event):
        if self.enable_select:
            plot = self.component
            index = plot.map_index((event.x, event.y), threshold=self.threshold)
            if index:
                plot.index.metadata["selection"] = index
                plot.value.metadata["selection"] = index
        return


# EOF
