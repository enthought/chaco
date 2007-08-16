

from enthought.traits.api import Property

# Local imports
from polygon_plot import PolygonPlot


def Alias(name):
    return Property(lambda obj: getattr(obj, name),
                    lambda obj, val: setattr(obj, name, val))

     
     
class FilledLinePlot(PolygonPlot):
    """ Draws a line plot filled to the axis """

    fill_color = Alias("face_color")

    def _render(self, gc, points):
        ox, oy = self.map_screen([[0,0]])[0]
        gc.save_state()

        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        gc.set_stroke_color(self.edge_color_)
        gc.set_line_width(self.edge_width)
        gc.set_line_dash(self.edge_style_)
        gc.set_fill_color(self.face_color_)

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
        else:
            gc.line_to(ox, endy)

        gc.close_path()
        gc.draw_path()

        gc.restore_state()



