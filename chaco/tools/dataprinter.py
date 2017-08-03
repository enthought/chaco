""" Defines the DataPrinter tool class.
"""

from __future__ import print_function

# Enthought library imports
from traits.api import Str
from enable.api import BaseTool

# Chaco imports
from chaco.api import BaseXYPlot


class DataPrinter(BaseTool):
    """ Simple listener tool that prints the (x,y) data space position of the
    point under the cursor.
    """

    # This tool is a listener, and does not display anything (overrides BaseTool).
    visible = False

    # Turn off drawing, because the tool prints to stdout.
    draw_mode = "none"

    # The string to format the (x,y) value in data space.
    format = Str("(%.3f, %.3f)")

    def normal_mouse_move(self, event):
        """ Handles the mouse being moved in the 'normal' state.

        Prints the data space position of the current mouse position.
        """
        plot = self.component
        if plot is not None:
            if isinstance(plot, BaseXYPlot):
                ndx = plot.map_index((event.x, event.y), index_only = True)
                x = plot.index.get_data()[ndx]
                y = plot.value.get_data()[ndx]
                print(self.format % (x,y))
            else:
                print("dataprinter: don't know how to handle plots of type", end=" ")
                print(plot.__class__.__name__)
        return


# EOF
