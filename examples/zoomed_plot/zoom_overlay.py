
from numpy import array, amax, amin, clip

from enthought.enable2.api import ColorTrait, Component
from enthought.traits.api import Float, Instance, Int
from enthought.chaco2.api import AbstractOverlay, BaseXYPlot


class ZoomOverlay(AbstractOverlay):
    """
    Draws a trapezoidal selection overlay from the source plot to the
    destination plot.  Assumes that the source plot lies above the destination
    plot.
    """
    
    source = Instance(BaseXYPlot)
    destination = Instance(Component)
    
    border_color = ColorTrait((0, 0, 0.7, 1))
    border_width = Int(1)
    fill_color = ColorTrait("dodgerblue")
    alpha = Float(0.3)
    
    def calculate_points(self, component):
        """
        Calculate the overlay polygon based on the selection and the location
        of the source and destination plots.
        """
        # find selection range on source plot
        x_start, x_end = self._get_selection_screencoords()
        if x_start > x_end:
            x_start, x_end = x_end, x_start
        
        y_end = self.source.y
        y_start = self.source.y2
        
        left_top = array([x_start, y_start])
        left_mid = array([x_start, y_end])
        right_top = array([x_end, y_start])
        right_mid = array([x_end, y_end])
        
        # Offset y because we want to avoid overlapping the trapezoid with the topmost
        # pixels of the destination plot.
        y = self.destination.y2 + 1
        
        left_end = array([self.destination.x, y])
        right_end = array([self.destination.x2, y])

        polygon = array((left_top, left_mid, left_end, 
                         right_end,right_mid, right_top))
        left_line = array((left_top, left_mid, left_end))
        right_line = array((right_end,right_mid, right_top))
        
        return left_line, right_line, polygon
    
    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """
        Draws this overlay onto 'component', rendering onto 'gc'.
        """

        tmp = self._get_selection_screencoords()
        if tmp is None:
            return
        
        left_line, right_line, polygon = self.calculate_points(component)
       
        gc.save_state()
        try:
            gc.translate_ctm(*component.position)
            gc.set_alpha(self.alpha)
            gc.set_fill_color(self.fill_color_)
            gc.set_line_width(self.border_width)
            gc.set_stroke_color(self.border_color_)
            gc.begin_path()
            gc.lines(polygon)
            gc.fill_path()
            
            gc.begin_path()
            gc.lines(left_line)
            gc.lines(right_line)
            gc.stroke_path()
        finally:
            gc.restore_state()
        return
    
    def _get_selection_screencoords(self):
        """
        Returns a tuple of (x1, x2) screen space coordinates of the start
        and end selection points.  If there is no current selection, then
        returns None.
        """
        selection = self.source.index.metadata["selections"]
        if selection is not None and len(selection) == 2:
            mapper = self.source.index_mapper
            return mapper.map_screen(array(selection))
        else:
            return None
    
    #------------------------------------------------------------------------
    # Trait event handlers
    #------------------------------------------------------------------------
    
    def _source_changed(self, old, new):
        if old is not None and old.controller is not None:
            old.controller.on_trait_change(self._selection_update_handler, "selection",
                                           remove=True)
        if new is not None and new.controller is not None:
            new.controller.on_trait_change(self._selection_update_handler, "selection")
        return
    
    def _selection_update_handler(self, value):
        if value is not None and self.destination is not None:
            r = self.destination.index_mapper.range
            start, end = amin(value), amax(value)
            r.low = start
            r.high = end
        
        self.source.request_redraw()
        self.destination.request_redraw()
        return
