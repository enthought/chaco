""" Defines the TrackingZoom class.
"""
from numpy import allclose, array, inf

# Enthought library imports
from enthought.enable2.api import ColorTrait, KeySpec
from enthought.traits.api import Enum, false, Float, Instance, Int, Trait, true, Tuple

# Chaco imports
from enthought.chaco2.tools.api import SimpleZoom

class TrackingZoom(SimpleZoom):
    """ Allows the user to zoom in or out on a plot that is using tracking.
    
    The **default_state** of the data range determines the tracking behavior.
    For example, if the data range's **default_state** is "low_track",
    the range's high value snaps to the right edge and the tracking, low, value 
    follows it by the data range's **tracking_amount** value (and vice versa
    for "high_track").
    """
    
 
    def normal_mouse_wheel(self, event):
        """ Handles the mouse wheel being used when the tool is in the 'normal'
        state.
        
        Overrides SimpleZoom.
        """
        if self.enable_wheel and event.mouse_wheel != 0:
            if event.mouse_wheel > 0:
                # zoom in
                zoom = 1.0 / (1.0 + 0.5 * self.wheel_zoom_step)
            elif event.mouse_wheel < 0:
                # zoom out
                zoom = 1.0 + 0.5 * self.wheel_zoom_step
                
            # We'll determine the current position of the cursor in dataspace,
            # then zoom in while trying to maintain the mouse screen coordinates
            # in the new range.
            c = self.component
            low_pt, high_pt = self._map_coordinate_box((c.x, c.y), (c.x2, c.y2))
            mouse_pos = (c.x_mapper.map_data(event.x), c.y_mapper.map_data(event.y))
            
            if self.tool_mode == "range":
                datarange_list = [(self._determine_axis(), self._get_mapper().range)]
            else:
                datarange_list = [(0, c.x_mapper.range), (1, c.y_mapper.range)]
            
            orig_low, orig_high = self._history[0]
            for ndx, datarange in datarange_list:
                mouse_val = mouse_pos[ndx]
                newlow = mouse_val - zoom * (mouse_val - low_pt[ndx])
                newhigh = mouse_val + zoom * (high_pt[ndx] - mouse_val)
                
                if type(orig_high) in (tuple,list):
                    ol, oh = orig_low[ndx], orig_high[ndx]
                else:
                    ol, oh = orig_low, orig_high
                
                if self._zoom_limit_reached(ol, oh, newlow, newhigh):
                    event.handled = True
                    return
                
                if datarange.default_state == 'low_track':
                    hi = max([source.get_bounds()[1] for source in datarange.sources])
                    #is hi in the current view?
                    if hi >= low_pt[ndx] and hi <= high_pt[ndx]:
                        datarange.scale_tracking_amount(zoom)
                        newhigh = 'auto'
                        newlow = 'track'

                elif datarange.default_state == 'high_track':
                    lo = min([source.get_bounds()[0] for source in datarange.sources])
                    #is lo in the current view?
                    if lo >= low_pt[ndx] and lo <= high_pt[ndx]:
                        datarange.scale_tracking_amount(zoom)
                        newlow = 'auto'
                        newhigh = 'track'
                
                datarange.set_bounds(newlow, newhigh)
            event.handled = True
            self.component.request_redraw()
        return
