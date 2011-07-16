
from traits.api import Enum, Float, List, Str
from enable.api import black_color_trait, ColorTrait, LineStyle

from chaco.sequence_projection_plot import SequenceProjectionPlot

class LineProjectionPlot(SequenceProjectionPlot):
    # The color of the line.
    color = black_color_trait

    # The color to use to highlight the line when selected.
    selected_color = ColorTrait("lightyellow")

    # The style of the selected line.
    selected_line_style = LineStyle("solid")

    # The name of the key in self.metadata that holds the selection mask
    metadata_name = Str("selections")

    # The thickness of the line.
    line_width = Float(1.0)

    # The line dash style.
    line_style = LineStyle

    # The rendering style of the line plot.
    #
    # connectedpoints
    #     "normal" style (default); each point is connected to subsequent and
    #     prior points by line segments
    # hold
    #     each point is represented by a line segment parallel to the abscissa
    #     (index axis) and spanning the length between the point and its
    #     subsequent point.
    # connectedhold
    #     like "hold" style, but line segments are drawn at each point of the
    #     plot to connect the hold lines of the prior point and the current
    #     point.  Also called a "right angle plot".
    render_style = Enum("connectedpoints", "hold", "connectedhold")

    def get_screen_points(self):
        #self._gather_points()
        #return [self.map_screen(ary) for ary in self.model.]
        return [self.map_screen(self.model.get_data())]

    def _render(self, gc, points, selected_points=None):
        print 'rendering'
        print points
        if len(points) == 0:
            return

        with gc:
            gc.set_antialias(True)
            gc.clip_to_rect(self.x, self.y, self.width, self.height)

            render_method_dict = {
                    "hold": self._render_hold,
                    "connectedhold": self._render_connected_hold,
                    "connectedpoints": self._render_normal
                    }
            render = render_method_dict.get(self.render_style, self._render_normal)

            if selected_points is not None:
                gc.set_stroke_color(self.selected_color_)
                gc.set_line_width(self.line_width+10.0)
                gc.set_line_dash(self.selected_line_style_)
                render(gc, selected_points, self.orientation)

            # Render using the normal style
            gc.set_stroke_color(self.color_)
            gc.set_line_width(self.line_width)
            gc.set_line_dash(self.line_style_)
            render(gc, points, self.orientation)

            # Draw the default axes, if necessary
            self._draw_default_axes(gc)

    @classmethod
    def _render_normal(cls, gc, points, orientation):
        for ary in points:
            if len(ary) > 0:
                gc.begin_path()
                gc.lines(ary)
                gc.stroke_path()
        return

    @classmethod
    def _render_hold(cls, gc, points, orientation):
        for starts in points:
            x,y = starts.T
            if orientation == "h":
                ends = transpose(array( (x[1:], y[:-1]) ))
            else:
                ends = transpose(array( (x[:-1], y[1:]) ))
            gc.begin_path()
            gc.line_set(starts[:-1], ends)
            gc.stroke_path()
        return

    @classmethod
    def _render_connected_hold(cls, gc, points, orientation):
        for starts in points:
            x,y = starts.T
            if orientation == "h":
                ends = transpose(array( (x[1:], y[:-1]) ))
            else:
                ends = transpose(array( (x[:-1], y[1:]) ))
            gc.begin_path()
            gc.line_set(starts[:-1], ends)
            gc.line_set(ends, starts[1:])
            gc.stroke_path()
        return
    