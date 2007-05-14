
# Enthought library imports
from enthought.traits.api import Any, Dict, Enum, Float, Instance
from enthought.traits.ui.api import View

# Chaco imports
from enthought.chaco2.api import BasePlotContainer, BaseTool, BaseXYPlot, \
                                OverlayPlotContainer, PlotAxis, PlotGrid, \
                                reverse_map_1d



class Fifo:
    """ Slightly-modified version of Fifo class from the python cookbook:
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/68436
    """
    def __init__(self):
        self.nextin = 0
        self.nextout = 0
        self.data = {}
    def append(self, value):
        self.data[self.nextin] = value
        self.nextin += 1
    def extend(self, values):
        if len(values) > 0:
            for i,val in enumerate(values):
                self.data[i+self.nextin] = val
            self.nextin += i+1
    def isempty(self):
        return self.nextout >= self.nextin
    def pop(self):
        value = self.data[self.nextout]
        del self.data[self.nextout]
        self.nextout += 1
        return value


def get_nested_components(container):
    """
    Returns a list of fundamental plotting components from a container
    with nested containers.  Performs a breadth-first search of the containment
    hierarchy.  Each element in the list is a tuple (component, (x,y)) where
    (x,y) is the coordinate frame offset of the component from the top-level
    container we are handed.
    """
    components = []
    worklist = Fifo()
    worklist.append((container, (0,0)))
    while 1:
        item, offset = worklist.pop()
        if isinstance(item, BasePlotContainer):
            new_offset = (offset[0]+item.x, offset[1]+item.y)
            for c in item.plot_components:
                worklist.append((c, new_offset))
        elif isinstance(item, PlotAxis) or isinstance(item, BaseXYPlot):
            components.append((item, offset))
        if worklist.isempty():
            break
    return components


class TraitsTool(BaseTool):
    """
    Tool to edit the traits of plots, grids, and axes.
    """
    
    draw_mode = "none"
    visible = False
    
    
    def normal_left_dclick(self, event):
        x = event.x
        y = event.y

        # First determine what component or components we are going to hittest
        # on.  If our component is an Axis or PlotRenderer of any sort,
        # then that is the only candidate.  If our component is a container,
        # then we add its non-container components to the list of candidates;
        # any nested containers are lower priority than primary plot components.
        candidates = []
        component = self.component
        if isinstance(component, BasePlotContainer):
            candidates = get_nested_components(self.component)
        elif isinstance(component, PlotAxis) or isinstance(component, BaseXYPlot):
            candidates = [(component, (0,0))]
        else:
            # We don't support clicking on unrecognized components
            return
        
        # Hittest against all the candidate and take the first one
        item = None
        for candidate, offset in candidates:
            if isinstance(candidate, PlotAxis):
                if candidate.is_in(x-offset[0], y-offset[1]):
                    item = candidate
                    break
            elif isinstance(candidate, BaseXYPlot):
                if candidate.hittest((x-offset[0], y-offset[1])):
                    item = candidate
                    break

        if item:
            self.component.active_tool = self
            item.edit_traits(kind="livemodal")
            event.handled = True
            self.component.active_tool = None
            item.request_redraw()
        return
    


# EOF
