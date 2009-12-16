import numpy

from enthought.enable.api import BaseTool, KeySpec
from enthought.traits.api import Enum, Float, Instance, Bool, HasTraits, List

from tool_history_mixin import ToolHistoryMixin

class ZoomState(HasTraits):
    """ A zoom state which can be applied and reverted.
    
        This class exists so that subclasses can introduce new types
        of events which can be applied and reverted in the same manner.
        This greatly eases the code for managing history
    """
    def __init__(self, old, new):
        self.old = old
        self.new = new
        
    def apply(self, zoom_tool):
        zoom_tool._zoom_in_mapper(zoom_tool.component.index_mapper, 
                                  self.new[0]/self.old[0])
        zoom_tool._zoom_in_mapper(zoom_tool.component.value_mapper, 
                                  self.new[1]/self.old[1])
        
        zoom_tool._index_factor = self.new[0]
        zoom_tool._value_factor = self.new[1]
    
    def revert(self, zoom_tool):
        zoom_tool._zoom_in_mapper(zoom_tool.component.index_mapper, 
                                  self.old[0]/self.new[0])
        zoom_tool._zoom_in_mapper(zoom_tool.component.value_mapper, 
                                  self.old[1]/self.new[1])

        zoom_tool._index_factor = self.old[0]
        zoom_tool._value_factor = self.old[1]

class BetterZoom(BaseTool, ToolHistoryMixin):
    
    # Keys to zoom in/out
    zoom_in_key = Instance(KeySpec, args=("+",))
    zoom_out_key = Instance(KeySpec, args=("-",))
    
    # Keys to zoom in/out in x direction only
    zoom_in_x_key = Instance(KeySpec, args=("Right", "shift"))
    zoom_out_x_key = Instance(KeySpec, args=("Left", "shift"))

    # Keys to zoom in/out in y direction only
    zoom_in_y_key = Instance(KeySpec, args=("Up", "shift"))
    zoom_out_y_key = Instance(KeySpec, args=("Down", "shift"))
    
    # Key to go to the previous state in the history.
    prev_state_key = Instance(KeySpec, args=("z", "control"))
    
    # Key to go to the next state in the history.
    next_state_key = Instance(KeySpec, args=("y", "control"))
    
    # Enable the mousewheel for zooming?
    enable_wheel = Bool(True)    
    
    # The axis to which the selection made by this tool is perpendicular. This
    # only applies in 'range' mode.
    axis = Enum("both", "index", "value")
    
    # The maximum ratio between the original data space bounds and the zoomed-in
    # data space bounds.  If None, then there is no limit (not advisable!).
    max_zoom_in_factor = Float(1e5, allow_none=True)

    # The maximum ratio between the zoomed-out data space bounds and the original
    # bounds.  If None, then there is no limit.
    max_zoom_out_factor = Float(1e5, allow_none=True)

    # The amount to zoom in by. The zoom out will be inversely proportional
    zoom_factor = 2.0

    # The zoom factor on each axis
    _index_factor = Float(1.0)
    _value_factor = Float(1.0)

    # inherited from ToolHistoryMixin, but requires instances of ZoomState
    _history = List(ZoomState, [ZoomState((1.0, 1.0), (1.0, 1.0))])
    
    #--------------------------------------------------------------------------
    #  public interface
    #--------------------------------------------------------------------------
    
    def zoom_in(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor
            
        new_index_factor = self._index_factor * factor
        new_value_factor = self._value_factor * factor
                    
        if self.axis == 'value':
            new_index_factor = self._index_factor
        elif self.axis == 'index':
            new_value_factor = self._value_factor
            
        zoom_state = ZoomState((self._index_factor, self._value_factor),
                               (new_index_factor, new_value_factor))
        
        zoom_state.apply(self)
        self._append_state(zoom_state)
    
    def zoom_out(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor
            
        new_index_factor = self._index_factor / factor
        new_value_factor = self._value_factor / factor
                    
        if self.axis == 'value':
            new_index_factor = self._index_factor
        elif self.axis == 'index':
            new_value_factor = self._value_factor
            
        zoom_state = ZoomState((self._index_factor, self._value_factor),
                               (new_index_factor, new_value_factor))
        
        zoom_state.apply(self)
        self._append_state(zoom_state)
                
    def zoom_in_x(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor

        if self.component.orientation == 'h':
            new_index_factor = self._index_factor * factor
            new_value_factor = self._value_factor
        else:
            new_index_factor = self._index_factor
            new_value_factor = self._value_factor * factor
            
        zoom_state = ZoomState((self._index_factor, self._value_factor),
                               (new_index_factor, new_value_factor))
        
        zoom_state.apply(self)            
        self._append_state(zoom_state)        

    def zoom_out_x(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor
            
        if self.component.orientation == 'h':
            new_index_factor = self._index_factor / factor
            new_value_factor = self._value_factor
        else:
            new_index_factor = self._index_factor
            new_value_factor = self._value_factor / factor
            
        zoom_state = ZoomState((self._index_factor, self._value_factor),
                               (new_index_factor, new_value_factor))
        
        zoom_state.apply(self)
        self._append_state(zoom_state)        

    def zoom_in_y(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor
            
        if self.component.orientation == 'v':
            new_index_factor = self._index_factor * factor
            new_value_factor = self._value_factor
        else:
            new_index_factor = self._index_factor
            new_value_factor = self._value_factor * factor
            
        zoom_state = ZoomState((self._index_factor, self._value_factor),
                               (new_index_factor, new_value_factor))
        
        zoom_state.apply(self)
        self._append_state(zoom_state)        

    def zoom_out_y(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor
            
        if self.component.orientation == 'v':
            new_index_factor = self._index_factor / factor
            new_value_factor = self._value_factor
        else:
            new_index_factor = self._index_factor
            new_value_factor = self._value_factor / factor
            
        zoom_state = ZoomState((self._index_factor, self._value_factor),
                               (new_index_factor, new_value_factor))
        
        zoom_state.apply(self)
            
        self._value_factor = new_value_factor
            
        self._append_state(zoom_state)        
        
    #--------------------------------------------------------------------------
    #  BaseTool interface
    #--------------------------------------------------------------------------
    
    def normal_key_pressed(self, event):
        """ Handles a key being pressed when the tool is in the 'normal'
        state.
        """
        if self.zoom_in_key.match(event):
            self.zoom_in()
            event.handled = True
        elif self.zoom_out_key.match(event):
            self.zoom_out()
            event.handled = True
        elif self.zoom_in_x_key.match(event):
            self.zoom_in_x(self.zoom_factor)
            event.handled = True
        elif self.zoom_out_x_key.match(event):
            self.zoom_out_x(self.zoom_factor)
            event.handled = True
        elif self.zoom_in_y_key.match(event):
            self.zoom_in_y(self.zoom_factor)
            event.handled = True
        elif self.zoom_out_y_key.match(event):
            self.zoom_out_y(self.zoom_factor)
            event.handled = True
            
        ToolHistoryMixin.normal_key_pressed(self, event)
        
        return
    
    def normal_mouse_wheel(self, event):
        if not self.enable_wheel:
            return
        
        if event.mouse_wheel != 0:
            if event.mouse_wheel > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.handled = True

    #--------------------------------------------------------------------------
    #  private interface
    #--------------------------------------------------------------------------

    def _zoom_in_mapper(self, mapper, factor):
        high = mapper.range.high
        low = mapper.range.low
        range = high-low
        center = numpy.mean((low, high))
        
        new_range = range/factor
        mapper.range.high = center + new_range/2
        mapper.range.low = center - new_range/2

    def _zoom_out_mapper(self, mapper, factor):
        high = mapper.range.high
        low = mapper.range.low
        range = high-low
        center = numpy.mean((low, high))

        new_range = range*factor
        mapper.range.high = center + new_range/2
        mapper.range.low = center - new_range/2
        
    def _get_x_mapper(self):
        if self.component.orientation == "h":
            return self.component.index_mapper
        return self.component.value_mapper

    def _get_y_mapper(self):
        if self.component.orientation == "h":
            return self.component.value_mapper
        return self.component.index_mapper
        
    #--------------------------------------------------------------------------
    #  ToolHistoryMixin interface
    #--------------------------------------------------------------------------

    def _next_state_pressed(self):
        """ Called when the tool needs to advance to the next state in the 
        stack.
        
        The **_history_index** will have already been set to the index 
        corresponding to the next state.
        """
        
        self._current_state().apply(self)

    def _prev_state_pressed(self):
        """ Called when the tool needs to advance to the previous state in the
        stack.
        
        The **_history_index** will have already been set to the index
        corresponding to the previous state.
        """
        self._history[self._history_index+1].revert(self)
    
    def _reset_state_pressed(self):
        """ Called when the tool needs to reset its history.  
        
        The history index will have already been set to 0.
        """
        for state in self._history[::-1]:
            state.revert(self)
            