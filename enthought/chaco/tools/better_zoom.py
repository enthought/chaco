import numpy

from enthought.enable.api import BaseTool, KeySpec
from enthought.traits.api import Enum, Float, Instance, Bool

from tool_history_mixin import ToolHistoryMixin

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

    _history = [(1.0, 1.0)]
    
    #--------------------------------------------------------------------------
    #  public interface
    #--------------------------------------------------------------------------
    
    def zoom_in(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor
        if self.axis != 'value':
            self._zoom_in_mapper(self.component.index_mapper, factor)
            self._index_factor *= factor
        if self.axis != 'index':
            self._zoom_in_mapper(self.component.value_mapper, factor)
            self._value_factor *= factor
            
        self._append_state((self._index_factor, self._value_factor))
    
    def zoom_out(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor
        if self.axis != 'value':
            self._zoom_out_mapper(self.component.index_mapper, factor)
            self._index_factor /= factor
        if self.axis != 'index':
            self._zoom_out_mapper(self.component.value_mapper, factor)
            self._value_factor /= factor
            
        self._append_state((self._index_factor, self._value_factor))
        
    def zoom_in_x(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor

        if self.component.orientation == "h":
            mapper = self.component.index_mapper
            self._zoom_in_mapper(mapper, factor)
            self._index_factor *= factor
        else:
            mapper = self.component.value_mapper
            self._zoom_in_mapper(mapper, factor)
            self._value_factor *= factor

        self._append_state((self._index_factor, self._value_factor))

    def zoom_out_x(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor

        if self.component.orientation == "h":
            mapper = self.component.index_mapper
            self._zoom_out_mapper(mapper, factor)
            self._index_factor /= factor
        else:
            mapper = self.component.value_mapper
            self._zoom_out_mapper(mapper, factor)
            self._value_factor /= factor

        self._append_state((self._index_factor, self._value_factor))

    def zoom_in_y(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor

        if self.component.orientation == "v":
            mapper = self.component.index_mapper
            self._zoom_in_mapper(mapper, factor)
            self._index_factor *= factor
        else:
            mapper = self.component.value_mapper
            self._zoom_in_mapper(mapper, factor)
            self._value_factor *= factor

        self._append_state((self._index_factor, self._value_factor))

    def zoom_out_y(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor

        if self.component.orientation == "v":
            mapper = self.component.index_mapper
            self._zoom_out_mapper(mapper, factor)
            self._index_factor /= factor
        else:
            mapper = self.component.value_mapper
            self._zoom_out_mapper(mapper, factor)
            self._value_factor /= factor
            
        self._append_state((self._index_factor, self._value_factor))
        
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
    
    def _update_from_state_change(self):
        index_factor, value_factor = self._current_state()
        
        self._zoom_in_mapper(self.component.index_mapper, 
                             index_factor/self._index_factor)
        self._zoom_in_mapper(self.component.value_mapper, 
                             value_factor/self._value_factor)
        
        self._index_factor = index_factor
        self._value_factor = value_factor
    
    #--------------------------------------------------------------------------
    #  ToolHistoryMixin interface
    #--------------------------------------------------------------------------

    def _next_state_pressed(self):
        """ Called when the tool needs to advance to the next state in the 
        stack.
        
        The **_history_index** will have already been set to the index 
        corresponding to the next state.
        """
        self._update_from_state_change()   

    def _prev_state_pressed(self):
        """ Called when the tool needs to advance to the previous state in the
        stack.
        
        The **_history_index** will have already been set to the index
        corresponding to the previous state.
        """
        self._update_from_state_change()           
    
    def _reset_state_pressed(self):
        """ Called when the tool needs to reset its history.  
        
        The history index will have already been set to 0.
        """
        self._update_from_state_change()   
