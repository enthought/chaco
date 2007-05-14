
# Major library imports
from numpy import array, float64, hstack, resize

# Enthought library imports
from enthought.traits.api import Instance, Bool, true

# Chaco import
from enthought.chaco2.api import BaseTool, ArrayDataSource


class DrawPointsTool(BaseTool):
    """
    DrawPointsTool draws points as they are clicked onto a rectangular
    plot.
    """
    
    xdata = Instance(ArrayDataSource)
    ydata = Instance(ArrayDataSource)
    activated = true
    
    #It would be nice to set the pointer to a cross
    
    def __init__(self, **kwtraits):
        BaseTool.__init__(self, **kwtraits)
        self.xdata = self.component.value1
        self.ydata = self.component.value2
        return
        
    def normal_left_down(self, event):
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
    
    