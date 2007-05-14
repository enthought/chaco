
# Enthought library imports
from enthought.traits.api import Any, Float, Str, Trait

# Chaco imports
from enthought.chaco2.api import BaseTool, BaseXYPlot

class DataPrinter(BaseTool):
    """
    Simple listener tool to dump out the (x,y) position of the point under the
    cursor.
    """
    
    # Since we are a listener and print output to stdout, we don't ever need
    # to draw.
    visible = False
    draw_mode = "none"
    
    # The string to use to format the x,y value that we find in data space
    format = Str("(%.3f, %.3f)")

    def normal_mouse_move(self, event):
        plot = self.component
        if plot is not None:
            if isinstance(plot, BaseXYPlot):
                ndx = plot.map_index((event.x, event.y), index_only = True)
                x = plot.index.get_data()[ndx]
                y = plot.value.get_data()[ndx]
                print self.format % (x,y)
            else:
                print "dataprinter: don't know how to handle plots of type",
                print plot.__class__.__name__
        return
    
    
# EOF
