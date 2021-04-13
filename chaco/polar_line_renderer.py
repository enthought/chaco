""" Defines the PolarLineRenderer class.
"""


# Major library imports
from numpy import array, cos, pi, sin, transpose

# Enthought library imports
from enable.api import black_color_trait, LineStyle
from traits.api import Float

# Local, relative imports
from .abstract_plot_renderer import AbstractPlotRenderer


class PolarLineRenderer(AbstractPlotRenderer):
    """A renderer for polar line plots."""

    # ------------------------------------------------------------------------
    # Appearance-related traits
    # ------------------------------------------------------------------------

    # The color of the origin axis.
    origin_axis_color_ = (0, 0, 0, 1)
    # The width of the origin axis.
    origin_axis_width = 2.0
    # The origin axis is visible.
    origin_axis_visible = True
    # The grid is visible.
    grid_visible = True
    # The orientation of the plot is horizontal; for any other value, it is
    # transposed
    orientation = "h"
    # The color of the line.
    color = black_color_trait
    # The width of the line.
    line_width = Float(1.0)
    # The style of the line.
    line_style = LineStyle("solid")
    # The style of the grid lines.
    grid_style = LineStyle("dot")

    def _gather_points(self):
        """
        Collects the data points that are within the plot bounds and caches them
        """
        # This is just a stub for now.  We should really find the lines only
        # inside the screen range here.

        x = self.index.get_data()
        y = self.value.get_data()
        rad = min(self.width / 2.0, self.height / 2.0)
        sx = x * rad + self.x + self.width / 2.0
        sy = y * rad + self.y + self.height / 2.0

        points = transpose(array((sx, sy)))
        self._cached_data_pts = points
        self._cache_valid = True

    def _data_changed(self):
        self._cache_valid = False

    def _update_mappers(self):
        # Dunno if there is anything else to do here
        self._cache_valid = False

    def _render(self, gc, points):
        """Actually draw the plot."""
        with gc:
            gc.set_antialias(True)
            self._draw_default_axes(gc)
            self._draw_default_grid(gc)
            if len(points) > 0:
                gc.clip_to_rect(self.x, self.y, self.width, self.height)
                gc.set_stroke_color(self.color_)
                gc.set_line_width(self.line_width)
                gc.set_line_dash(self.line_style_)

                gc.begin_path()
                gc.lines(points)
                gc.stroke_path()

    def map_screen(self, data_array):
        """Maps an array of data points into screen space and returns it as
        an array.

        Implements the AbstractPlotRenderer interface.
        """

        if len(data_array) == 0:
            return []
        elif len(data_array) == 1:
            xtmp, ytmp = transpose(data_array)
            x_ary = xtmp
            y_ary = ytmp
        else:
            x_ary, y_ary = transpose(data_array)

        sx = self.index_mapper.map_screen(x_ary)
        sy = self.value_mapper.map_screen(y_ary)

        if self.orientation == "h":
            return transpose(array((sx, sy)))
        else:
            return transpose(array((sy, sx)))

    def map_data(self, screen_pt):
        """Maps a screen space point into the "index" space of the plot.

        Implements the AbstractPlotRenderer interface.
        """
        if self.orientation == "h":
            x, y = screen_pt
        else:
            y, x = screen_pt
        return array(
            (self.index_mapper.map_data(x), self.value_mapper.map_data(y))
        )

    def _downsample(self):
        return self.map_screen(self._cached_data_pts)

    def _draw_plot(self, *args, **kw):
        """Draws the 'plot' layer."""
        # Simple compatibility with new-style rendering loop
        return self._draw_component(*args, **kw)

    def _draw_component(self, gc, view_bounds=None, mode="normal"):
        """Renders the component."""
        self._gather_points()
        self._render(gc, self._cached_data_pts)

    def _bounds_changed(self, old, new):
        super(PolarLineRenderer, self)._bounds_changed(old, new)
        self._update_mappers()

    def _bounds_items_changed(self, event):
        super(PolarLineRenderer, self)._bounds_items_changed(event)
        self._update_mappers()

    def _draw_default_axes(self, gc):
        if not self.origin_axis_visible:
            return

        with gc:
            gc.set_stroke_color(self.origin_axis_color_)
            gc.set_line_width(self.origin_axis_width)
            gc.set_line_dash(self.grid_style_)
            x_data, y_data = transpose(self._cached_data_pts)
            x_center = self.x + self.width / 2.0
            y_center = self.y + self.height / 2.0

            for theta in range(12):
                r = min(self.width / 2.0, self.height / 2.0)
                x = r * cos(theta * pi / 6) + x_center
                y = r * sin(theta * pi / 6) + y_center
                data_pts = array([[x_center, y_center], [x, y]])
                start, end = data_pts
                gc.move_to(int(start[0]), int(start[1]))
                gc.line_to(int(end[0]), int(end[1]))
                gc.stroke_path()

    def _draw_default_grid(self, gc):
        if not self.grid_visible:
            return

        with gc:
            gc.set_stroke_color(self.origin_axis_color_)
            gc.set_line_width(self.origin_axis_width)
            gc.set_line_dash(self.grid_style_)
            x_data, y_data = transpose(self._cached_data_pts)
            x_center = self.x + self.width / 2.0
            y_center = self.y + self.height / 2.0
            rad = min(self.width / 2.0, self.height / 2.0)
            for r_part in range(1, 5):
                r = rad * r_part / 4
                gc.arc(x_center, y_center, r, 0, 2 * pi)
                gc.stroke_path()
