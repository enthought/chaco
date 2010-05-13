

from enthought.traits.api import Property, Enum

# Local imports
from polygon_plot import PolygonPlot


def Alias(name):
    return Property(lambda obj: getattr(obj, name),
                    lambda obj, val: setattr(obj, name, val))

     
     
class FilledLinePlot(PolygonPlot):
    """ Draws a line plot filled to the axis """

    fill_color = Alias("face_color")
    
    # Direction to fill. Down is towards the origin, up is towards the max
    fill_direction = Enum("down", "up")

    def _render(self, gc, points):
        if len(points) == 0:
            return

        if self.fill_direction == 'down':
            ox, oy = self.map_screen([[0,0]])[0]
        else:
            ox, oy = self.map_screen([[self.x_mapper.range.high, 
                                      self.y_mapper.range.high]])[0]
        gc.save_state()
        
        try:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
    
            # If the fill color is not transparent, then draw the fill polygon first
            face_col = self.face_color_
            if not (len(face_col) == 4 and face_col[-1] == 0):
                gc.set_fill_color(face_col)
                gc.begin_path()
                startx, starty = points[0]
                if self.orientation == "h":
                    gc.move_to(startx, oy)
                    gc.line_to(startx, starty)
                else:
                    gc.move_to(ox, starty)
                    gc.line_to(startx, starty)
                
                gc.lines(points)
    
                endx, endy = points[-1]
                if self.orientation == "h":
                    gc.line_to(endx, oy)
                    gc.line_to(startx, oy)
                else:
                    gc.line_to(ox, endy)
                    gc.line_to(ox, starty)
    
                gc.close_path()
                gc.fill_path()
    
            # If the line color is not transparent, or tha same color
            # as the filled area:
            edge_col = self.edge_color_
            if (not (len(edge_col) == 4 and edge_col[-1] == 0)) and edge_col != face_col:
                gc.set_stroke_color(edge_col)
                gc.set_line_width(self.edge_width)
                gc.set_line_dash(self.edge_style_)
                gc.begin_path()
                gc.move_to(*points[0])
                gc.lines(points)
                gc.stroke_path()
                
        finally:
            gc.restore_state()



