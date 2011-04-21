""" Defines the DrawPointsTool class.
"""
# Major library imports
from numpy import array, float64, hstack

# Enthought library imports
from traits.api import Instance, Bool
from enthought.enable.api import BaseTool

# Chaco import
from enthought.chaco.api import ArrayDataSource


class DrawPointsTool(BaseTool):
    """ A tool that draws points onto a rectangular plot as they are clicked.
    """

    # A data source for the x-dimension of the drawn points.
    xdata = Instance(ArrayDataSource)
    # A data source for the y-dimension of the drawn points.
    ydata = Instance(ArrayDataSource)
    # Is this the active tool?
    activated = Bool(True)

    #It would be nice to set the pointer to a cross

    def __init__(self, **kwtraits):
        BaseTool.__init__(self, **kwtraits)
        self.xdata = self.component.value1
        self.ydata = self.component.value2
        return

    def normal_left_down(self, event):
        """ Handles the left mouse button being clicked when the tool is in the
        'normal' state.

        Maps the event position into data space, adds the point to the points
        for this tool, and redraws.
        """
        x,y = event.x, event.y
        data_x, data_y = self.component.map_data((x,y))
        self._append_data(self.xdata, data_x)
        self._append_data(self.ydata, data_y)
        self.component.request_redraw()
        return

    def _activate(self):
        self.activated = True
        return

    def _deactivate(self):
        self.activated = False
        return

    def _append_data(self, datasource, data):
        olddata = array(datasource.get_data(), float64)
        newdata = hstack((olddata, data))
        datasource.set_data(newdata)
        return


#EOF


