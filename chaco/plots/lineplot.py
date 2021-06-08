# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the LinePlot class.
"""


# Standard library imports
import warnings

# Major library imports
from numpy import (
    argsort,
    array,
    concatenate,
    inf,
    invert,
    isnan,
    take,
    transpose,
    zeros,
    sqrt,
    argmin,
    clip,
    column_stack,
)

# Enthought library imports
from enable.api import black_color_trait, ColorTrait, LineStyle
from traits.api import Enum, Float, List, Str, Property, Tuple, cached_property
from traitsui.api import Item, View

# Local relative imports
from chaco.base import arg_find_runs, arg_true_runs, reverse_map_1d, intersect_range
from chaco.base_xy_plot import BaseXYPlot


class LinePlot(BaseXYPlot):
    """A plot consisting of a line.

    This is the most fundamental object to use to create line plots. However,
    it is somewhat low-level and therefore creating one properly to do what
    you want can require some verbose code. The create_line_plot() function
    in plot_factory.py can hide some of this verbosity for common cases.
    """

    #: The color of the line.
    color = black_color_trait(requires_redraw=True)

    #: The RGBA tuple for rendering lines. It is always a tuple of length 4.
    #: It has the same RGB values as :attr:`color`, and its alpha value is the
    #: alpha value of self.color multiplied by self.alpha.
    effective_color = Property(Tuple, observe=["color", "alpha"])

    #: The color to use to highlight the line when selected.
    selected_color = ColorTrait("lightyellow")

    #: The style of the selected line.
    selected_line_style = LineStyle("solid")

    #: The name of the key in self.metadata that holds the selection mask
    metadata_name = Str("selections")

    #: The thickness of the line.
    line_width = Float(1.0, requires_redraw=True)

    #: The line dash style.
    line_style = LineStyle(requires_redraw=True)

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

    #: TraitsUI View for customizing the plot.
    traits_view = View(
        Item("color", style="custom"),
        "line_width",
        "line_style",
        buttons=["OK", "Cancel"],
    )

    # ------------------------------------------------------------------------
    # Private traits
    # ------------------------------------------------------------------------

    # Cached list of non-NaN arrays of (x,y) data-space points; regardless of
    # self.orientation, this is always stored as (index_pt, value_pt).  This is
    # different from the default BaseXYPlot definition.
    _cached_data_pts = List

    # Cached list of non-NaN arrays of (x,y) screen-space points.
    _cached_screen_pts = List

    def hittest(self, screen_pt, threshold=7.0, return_distance=False):
        """
        Tests whether the given screen point is within *threshold* pixels of
        any data points on the line.  If so, then it returns the (x,y) value of
        a data point near the screen point.  If not, then it returns None.
        """

        # First, check screen_pt is directly on a point in the lineplot
        ndx = self.map_index(screen_pt, threshold)
        if ndx is not None:
            # screen_pt is one of the points in the lineplot
            data_pt = (self.index.get_data()[ndx], self.value.get_data()[ndx])
            if return_distance:
                scrn_pt = self.map_screen(data_pt)[0]
                dist = sqrt(
                    (screen_pt[0] - scrn_pt[0]) ** 2
                    + (screen_pt[1] - scrn_pt[1]) ** 2
                )
                return (data_pt[0], data_pt[1], dist)
            else:
                return data_pt
        else:
            # We now must check the lines themselves

            # Must check all lines within threshold along the major axis,
            # so determine the bounds of the region of interest in dataspace
            if self.orientation == "h":
                dmax = self.map_data((screen_pt[0] + threshold, screen_pt[1]))
                dmin = self.map_data((screen_pt[0] - threshold, screen_pt[1]))
            else:
                dmax = self.map_data((screen_pt[0], screen_pt[1] + threshold))
                dmin = self.map_data((screen_pt[0], screen_pt[1] - threshold))

            xmin, xmax = self.index.get_bounds()

            # Now compute the bounds of the region of interest as indexes
            if dmin < xmin:
                ndx1 = 0
            elif dmin > xmax:
                ndx1 = len(self.value.get_data()) - 1
            else:
                ndx1 = reverse_map_1d(
                    self.index.get_data(), dmin, self.index.sort_order
                )
            if dmax < xmin:
                ndx2 = 0
            elif dmax > xmax:
                ndx2 = len(self.value.get_data()) - 1
            else:
                ndx2 = reverse_map_1d(
                    self.index.get_data(), dmax, self.index.sort_order
                )

            start_ndx = max(0, min(ndx1-1, ndx2-1))
            end_ndx = min(
                len(self.value.get_data()) - 1, max(ndx1 + 1, ndx2 + 1)
            )

            # Compute the distances to all points in the range of interest
            start = array(
                [
                    self.index.get_data()[start_ndx:end_ndx],
                    self.value.get_data()[start_ndx:end_ndx],
                ]
            )
            end = array(
                [
                    self.index.get_data()[start_ndx + 1 : end_ndx + 1],
                    self.value.get_data()[start_ndx + 1 : end_ndx + 1],
                ]
            )

            # Convert to screen points
            s_start = transpose(self.map_screen(transpose(start)))
            s_end = transpose(self.map_screen(transpose(end)))

            # t gives the parameter of the closest point to screen_pt
            # on the line going from s_start to s_end
            t = _closest_point(screen_pt, s_start, s_end)

            # Restrict to points on the line segment s_start->s_end
            t = clip(t, 0, 1)

            # Gives the corresponding point on the line
            px, py = _t_to_point(t, s_start, s_end)

            # Calculate distances
            dist = sqrt((px - screen_pt[0]) ** 2 + (py - screen_pt[1]) ** 2)

            # Find the minimum
            n = argmin(dist)
            # And return if it is good
            if dist[n] <= threshold:
                best_pt = self.map_data((px[n], py[n]), all_values=True)

                if return_distance:
                    return [best_pt[0], best_pt[1], dist[n]]
                else:
                    return best_pt

            return None

    def interpolate(self, index_value):
        """
        Returns the value of the plot at the given index value in screen space.
        Raises an IndexError when *index_value* exceeds the bounds of indexes on
        the value.
        """

        if self.index is None or self.value is None:
            raise IndexError(
                "cannot index when data source index or value is None"
            )

        index_data = self.index.get_data()
        value_data = self.value.get_data()

        ndx = reverse_map_1d(index_data, index_value, self.index.sort_order)

        # quick test to see if this value is already in the index array
        if index_value == index_data[ndx]:
            return value_data[ndx]

        # get x and y values to interpolate between
        if index_value < index_data[ndx]:
            x0 = index_data[ndx - 1]
            y0 = value_data[ndx - 1]
            x1 = index_data[ndx]
            y1 = value_data[ndx]
        else:
            x0 = index_data[ndx]
            y0 = value_data[ndx]
            x1 = index_data[ndx + 1]
            y1 = value_data[ndx + 1]

        if x1 != x0:
            slope = float(y1 - y0) / float(x1 - x0)
            dx = index_value - x0
            yp = y0 + slope * dx
        else:
            yp = inf

        return yp

    def get_screen_points(self):
        self._gather_points()
        if self.use_downsampling:
            return self._downsample()
        else:
            return [self.map_screen(ary) for ary in self._cached_data_pts]

    # ------------------------------------------------------------------------
    # Private methods; implements the BaseXYPlot stub methods
    # ------------------------------------------------------------------------

    def _gather_points(self):
        """
        Collects the data points that are within the bounds of the plot and
        caches them.
        """
        if not self._cache_valid:

            if self.index is None or self.value is None:
                return

            index = self.index.get_data()
            value = self.value.get_data()

            # Check to see if the data is completely outside the view region
            for ds, rng in (
                (self.index, self.index_range),
                (self.value, self.value_range),
            ):
                low, high = ds.get_bounds()
                if low > rng.high or high < rng.low:
                    self._cached_data_pts = []
                    self._cached_valid = True
                    return

            if len(index) == 0 or len(value) == 0 or len(index) != len(value):
                self._cached_data_pts = []
                self._cache_valid = True

            size_diff = len(value) - len(index)
            if size_diff > 0:
                warnings.warn(
                    "Chaco.LinePlot: len(value) %d - len(index) %d = %d\n"
                    % (len(value), len(index), size_diff)
                )
                index_max = len(index)
                value = value[:index_max]
            else:
                index_max = len(value)
                index = index[:index_max]

            # TODO: restore the functionality of rendering highlighted portions
            # of the line
            # selection = self.index.metadata.get(self.metadata_name, None)
            # if selection is not None and type(selection) in (ndarray, list) and \
            #        len(selection) > 0:

            # Split the index and value raw data into non-NaN chunks
            mask = invert(isnan(value)) & invert(isnan(index))

            # throw out index and value points outside the visible region
            mask = intersect_range(
                index, self.index_range.low, self.index_range.high, mask
            )
            mask = intersect_range(
                value, self.value_range.low, self.value_range.high, mask
            )

            points = [
                column_stack([index[start:end], value[start:end]])
                for start, end in arg_true_runs(mask)
            ]

            self._cached_data_pts = points
            self._cache_valid = True

    def _downsample(self):
        if not self._screen_cache_valid:
            m = self.index_mapper
            delta_screen = int(m.high_pos - m.low_pos)
            if delta_screen == 0:
                downsampled = []
            else:
                # TODO: implement other downsampling methods
                from chaco.downsample.lttb import (
                    largest_triangle_three_buckets,
                )

                downsampled = [
                    largest_triangle_three_buckets(p, delta_screen)
                    for p in self._cached_data_pts
                ]

            self._cached_screen_pts = [self.map_screen(p) for p in downsampled]
            self._screen_cache_valid = True

        return self._cached_screen_pts

    def _render(self, gc, points, selected_points=None):
        if len(points) == 0:
            return

        with gc:
            gc.set_antialias(True)
            gc.clip_to_rect(self.x, self.y, self.width, self.height)

            render_method_dict = {
                "hold": self._render_hold,
                "connectedhold": self._render_connected_hold,
                "connectedpoints": self._render_normal,
            }
            render = render_method_dict.get(
                self.render_style, self._render_normal
            )

            if selected_points is not None:
                gc.set_stroke_color(self.selected_color_)
                gc.set_line_width(self.line_width + 10.0)
                gc.set_line_dash(self.selected_line_style_)
                render(gc, selected_points, self.orientation)

            # Render using the normal style
            gc.set_stroke_color(self.effective_color)
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

    @classmethod
    def _render_hold(cls, gc, points, orientation):
        for starts in points:
            x, y = starts.T
            if orientation == "h":
                ends = transpose(array((x[1:], y[:-1])))
            else:
                ends = transpose(array((x[:-1], y[1:])))
            gc.begin_path()
            gc.line_set(starts[:-1], ends)
            gc.stroke_path()

    @classmethod
    def _render_connected_hold(cls, gc, points, orientation):
        for starts in points:
            x, y = starts.T
            if orientation == "h":
                ends = transpose(array((x[1:], y[:-1])))
            else:
                ends = transpose(array((x[:-1], y[1:])))
            gc.begin_path()
            gc.line_set(starts[:-1], ends)
            gc.line_set(ends, starts[1:])
            gc.stroke_path()

    def _render_icon(self, gc, x, y, width, height):
        with gc:
            gc.set_stroke_color(self.effective_color)
            gc.set_line_width(self.line_width)
            gc.set_line_dash(self.line_style_)
            gc.set_antialias(0)
            gc.move_to(x, y + height / 2)
            gc.line_to(x + width, y + height / 2)
            gc.stroke_path()

    def _downsample_vectorized(self):
        """
        Analyzes the screen-space points stored in self._cached_data_pts
        and replaces them with a downsampled set.
        """
        pts = self._cached_screen_pts  # .astype(int)

        # some boneheaded short-circuits
        m = self.index_mapper
        if (pts.shape[0] < 400) or (pts.shape[0] < m.high_pos - m.low_pos):
            return

        pts2 = concatenate((array([[0.0, 0.0]]), pts[:-1]))
        z = abs(pts - pts2)
        d = z[:, 0] + z[:, 1]
        # ... TODO ...

    @cached_property
    def _get_effective_color(self):
        alpha = self.color_[-1] if len(self.color_) == 4 else 1
        c = self.color_[:3] + (alpha * self.alpha,)
        return c


def _closest_point(target, p1, p2):
    """Utility function for hittest:
    finds the point on the line between p1 and p2 to
    the target. Returns the 't' value of that point
    where the line is parametrized as
        t -> p1*(1-t) + p2*t
    Notably, if t=0 is p1, t=2 is p2 and anything outside
    that range is a point outisde p1, p2 on the line
    Note: can divide by zero, so user should check for that"""
    t = (
        (p1[0] - target[0]) * (p1[0] - p2[0])
        + (p1[1] - target[1]) * (p1[1] - p2[1])
    ) / ((p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1]))
    return t


def _t_to_point(t, p1, p2):
    """utility function for hittest for use with _closest_point
    returns the point corresponding to the parameter t
    on the line going between p1 and p2"""
    return (p1[0] * (1 - t) + p2[0] * t, p1[1] * (1 - t) + p2[1] * t)
