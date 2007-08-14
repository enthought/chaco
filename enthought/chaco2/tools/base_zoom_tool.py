""" Defines the base class for various types of zoom tools.
"""

from numpy import allclose, inf

# Enthought library imports
from enthought.traits.api import Enum, Float, HasTraits

class BaseZoomTool(HasTraits):
    """ Defines traits and methods to actually perform the logic of zooming
    onto a plot.
    """
    
    # If the tool only applies to a particular axis, this attribute is used to
    # determine which mapper and range to use.
    axis = Enum("index", "value")

    # The maximum ratio between the original data space bounds and the zoomed-in
    # data space bounds.  If None, then there is no limit (not advisable!).
    max_zoom_in_factor = Float(1e5, allow_none=True)

    # The maximum ratio between the zoomed-out data space bounds and the original
    # bounds.  If None, then there is no limit.
    max_zoom_out_factor = Float(1e5, allow_none=True)
    
    def _zoom_limit_reached(self, orig_low, orig_high, new_low, new_high):
        """ Returns True if the new low and high exceed the maximum zoom
        limits
        """
        orig_bounds = orig_high - orig_low

        if orig_bounds == inf:
            # There isn't really a good way to handle the case when the
            # original bounds were infinite, since any finite zoom
            # range will certainly exceed whatever zoom factor is set.
            # In this case, we just allow unbounded levels of zoom.
            return False
        
        new_bounds = new_high - new_low
        if allclose(orig_bounds, 0.0):
            return True
        if allclose(new_bounds, 0.0):
            return True
        if (new_bounds / orig_bounds) > self.max_zoom_out_factor or \
           (orig_bounds / new_bounds) > self.max_zoom_in_factor:
            return True
        return False

    #------------------------------------------------------------------------
    # Utility methods for computing axes, coordinates, etc.
    #------------------------------------------------------------------------

    def _get_mapper(self):
        """ Returns the mapper for the component associated with this tool.
        
        The zoom tool really only cares about this, so subclasses can easily
        customize SimpleZoom to work with all sorts of components just by
        overriding this method.
        """
        return getattr(self.component, self.axis + "_mapper")
        

    def _get_axis_coord(self, event, axis="index"):
        """ Returns the coordinate of the event along the axis of interest
        to the tool (or along the orthogonal axis, if axis="value").
        """
        event_pos = (event.x, event.y)
        if axis == "index":
            return event_pos[ self._determine_axis() ]
        else:
            return event_pos[ 1 - self._determine_axis() ]

    def _determine_axis(self):
        """ Determines whether the index of the coordinate along the axis of
        interest is the first or second element of an (x,y) coordinate tuple.
        """
        if self.axis == "index":
            if self.component.orientation == "h":
                return 0
            else:
                return 1
        else:   # self.axis == "value"
            if self.component.orientation == "h":
                return 1
            else:
                return 0

    def _map_coordinate_box(self, start, end):
        """ Given start and end points in screen space, returns corresponding
        low and high points in data space.
        """
        low = [0,0]
        high = [0,0]
        for axis_index, mapper in [(0, self.component.x_mapper), \
                                   (1, self.component.y_mapper)]:
            low_val = mapper.map_data(start[axis_index])
            high_val = mapper.map_data(end[axis_index])
            
            if low_val > high_val:
                low_val, high_val = high_val, low_val
            low[axis_index] = low_val
            high[axis_index] = high_val
        return low, high
    
