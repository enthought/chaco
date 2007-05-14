
# Major library imports
from numpy import array, take, transpose

# Enthought library imports
from enthought.enable2.api import ColorTrait
from enthought.traits.api import Any, Enum, false, Float, Str, Trait

# Chaco imports
from enthought.chaco2.api import BaseTool, BaseXYPlot

class PointMarker(BaseTool):
    """
    This tool looks at an X-Y plot's index datasource and draws a
    line corresponding to the index indicated by the "selections" metadata.
    """

    # The axis to which this tool is parallel
    axis = Enum("index", "value")
    
    # Should the line inspector write the current point to the appropriate
    # datasource's metadata?
    
    # Configure our BaseTool traits
    visible = True
    draw_mode = "overlay"
    
    # TODO:STYLE
    color = ColorTrait("red")
    line_width = Float(1.0)

    def draw(self, gc, view_bounds=None):
        # Draw the component in interactive mode
        plot = self.component
        if plot is not None:
            # selections should be a list of indices on the datasource
            indices = getattr(plot, self.axis).metadata["selections"]
            
            if len(indices) == 0:
                return
            
            index_pts = take(plot.index.get_data(), indices)
            value_pts = take(plot.value.get_data(), indices)
            data_pts = transpose(array((index_pts, value_pts)))
            screen_pts = plot.map_screen(data_pts)
            
            if self.axis == "index":
                if plot.orientation == "h":
                    self._draw_vertical_lines(gc, screen_pts)
                else:
                    self._draw_horizontal_lines(gc, screen_pts)
            else:   # self.axis == "value"
                if plot.orientation == "h":
                    self._draw_horizontal_lines(gc, screen_pts)
                else:
                    self._draw_vertical_lines(gc, screen_pts)
        return
    
    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _draw_vertical_lines(self, gc, points):
        gc.save_state()
        try:
            gc.set_stroke_color(self.color_)
            for pt in points:
                gc.move_to(int(pt[0])+0.5, self.component.y)
                gc.line_to(int(pt[0])+0.5, self.component.y2)
            gc.stroke_path()
        finally:
            gc.restore_state()
        return
    
    def _draw_horizontal_lines(self, gc, points):
        gc.save_state()
        try:
            gc.set_stroke_color(self.color_)
            for pt in points:
                gc.move_to(self.component.x, int(pt[1])+0.5)
                gc.line_to(self.component.x2, int(pt[1])+0.5)
            gc.stroke_path()
        finally:
            gc.restore_state()
        return

    
    
# EOF
