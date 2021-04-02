from numpy import empty
from traits.api import Property, Enum

# Local imports
from .lineplot import LinePlot
from .polygon_plot import PolygonPlot


def Alias(name):
    return Property(
        lambda obj: getattr(obj, name),
        lambda obj, val: setattr(obj, name, val),
    )


class FilledLinePlot(PolygonPlot):
    """ Draws a line plot filled to the axis """

    fill_color = Alias("face_color")

    #: Direction to fill. Down is towards the origin, up is towards the max
    fill_direction = Enum("down", "up")

    #: The rendering style of the line plot.
    #:
    #: connectedpoints
    #:     "normal" style (default); each point is connected to subsequent and
    #:     prior points by line segments
    #: hold
    #:     each point is represented by a line segment parallel to the abscissa
    #:     (index axis) and spanning the length between the point and its
    #:     subsequent point.
    #: connectedhold
    #:     like "hold" style, but line segments are drawn at each point of the
    #:     plot to connect the hold lines of the prior point and the current
    #:     point.  Also called a "right angle plot".
    render_style = Enum("connectedpoints", "hold", "connectedhold")

    def _render(self, gc, points):
        if len(points) == 0:
            return

        render_method_dict = {
            "hold": LinePlot._render_hold,
            "connectedhold": LinePlot._render_connected_hold,
            "connectedpoints": LinePlot._render_normal,
        }
        render_lines = render_method_dict.get(
            self.render_style, LinePlot._render_normal
        )

        if self.fill_direction == "down":
            ox, oy = self.map_screen([[0, 0]])[0]
        else:
            ox, oy = self.map_screen(
                [[self.x_mapper.range.high, self.y_mapper.range.high]]
            )[0]

        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)

            # If the fill color is not transparent, then draw the fill polygon first
            face_col = self.effective_face_color
            if not (len(face_col) == 4 and face_col[-1] == 0):
                if self.render_style in ("hold", "connectedhold"):
                    # Modify the points array before passing it in to render_polys:
                    # Between every two points, create an intermediate point with
                    # the first point's Y and the second point's X.  (For vertical
                    # plots, use the first point's X and the second point's Y.)
                    new_points = empty((points.shape[0] * 2 - 1, 2))
                    new_points[::2] = points
                    if self.orientation == "h":
                        new_points[1::2, 0] = points[1:, 0]
                        new_points[1::2, 1] = points[:-1, 1]
                    else:
                        new_points[1::2, 0] = points[:-1, 0]
                        new_points[1::2, 1] = points[1:, 1]
                    points = new_points

                self._render_polys(gc, points, ox, oy)

            # If the line color is not transparent, or tha same color
            # as the filled area:
            edge_col = self.effective_edge_color
            if (
                not (len(edge_col) == 4 and edge_col[-1] == 0)
            ) and edge_col != face_col:
                gc.set_stroke_color(edge_col)
                gc.set_line_width(self.edge_width)
                gc.set_line_dash(self.edge_style_)
                # Create a list around points because the LinePlot supports
                # Nans, and its rendering methods expect lists of disjoint arrays.
                render_lines(gc, [points], self.orientation)

    def _render_polys(self, gc, points, ox, oy):
        face_col = self.effective_face_color
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
