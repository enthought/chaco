
from __future__ import with_statement

import six
import six.moves as sm

# Major library imports
from numpy import column_stack, compress, invert, isnan, transpose
import logging

# Enthought library imports
from traits.api import Any, Enum, Float, Instance

# Chaco imports
from .lineplot import LinePlot
from .abstract_data_source import AbstractDataSource

# Set up a logger for this module
logger = logging.getLogger(__name__)



class ErrorBarPlot(LinePlot):
    """ Renders errorbars at various points.
    """

    #: The datasource containing the low values
    value_low = Instance(AbstractDataSource)

    #: The datasource containing the high values
    value_high = Instance(AbstractDataSource)

    #: The screen-space width of the endcap bars
    endcap_size = Float(5.0)

    #: The kind of encap to render on error bars
    endcap_style = Enum("bar", "none", None)

    # Override the inherited trait definition
    _cached_data_pts = Any

    def map_screen(self, data_array):
        """ data_array can be Nx2 or Nx3.  In the former case, each row is
        treated as (index, value), and this method returns screen X and Y
        coordinates.  In the latter case, each row is treated as (index,
        value_low, value_high), and the method returns either (x, ylow, yhigh)
        or (y, xlow, xhigh) depending on self.orientation.
        """
        if len(data_array) == 0:
            return []
        elif data_array.shape[1] == 2:
            return LinePlot.map_screen(self, data_array)
        else:
            x, ylow, yhigh = transpose(data_array)
            sx = self.index_mapper.map_screen(x)
            sylow = self.value_mapper.map_screen(ylow)
            syhigh = self.value_mapper.map_screen(yhigh)
            return column_stack((sx, sylow, syhigh))

    def get_screen_points(self):
        self._gather_points()
        return self.map_screen(self._cached_data_pts)

    def _gather_points(self):

        if self._cache_valid:
            return

        if not self.index or not self.value_low or not self.value_high:
            return

        index, index_mask = self.index.get_data_mask()
        value_low, value_low_mask = self.value_low.get_data_mask()
        value_high, value_high_mask = self.value_high.get_data_mask()
        value_mask = value_low_mask & value_high_mask

        l1, l2, l3 = sm.map(len, (index, value_low, value_high))
        if 0 in (l1, l2, l3) or not (l1 == l2 == l3):
            logger.warning(
                "Chaco: using empty dataset; index_len=%d, "
                "value_low_len=%d, value_high_len=%d."
                % (l1,l2,l3)
            )
            self._cached_data_pts = []
            self._cache_valid = True
            return

        index_range_mask = self.index_mapper.range.mask_data(index)
        value_low_mask = self.value_mapper.range.mask_data(value_low)
        value_high_mask = self.value_mapper.range.mask_data(value_high)
        value_range_mask = value_low_mask | value_high_mask

        nan_mask = invert(isnan(index_mask) | isnan(value_mask))
        point_mask = index_mask & value_mask & nan_mask & index_range_mask & value_range_mask

        points = column_stack((index, value_low, value_high))

        self._cached_data_pts = compress(point_mask, points, axis=0)
        self._cache_valid = True
        return

    def _render(self, gc, points, icon_mode=False):
        if len(points) == 0:
            return

        if not icon_mode:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)

        with gc:
            gc.set_antialias(False)
            gc.set_stroke_color(self.color_)
            gc.set_line_width(self.line_width)
            gc.set_line_dash(self.line_style_)

            if self.orientation == "h":
                x, ylow, yhigh = transpose(points)
                start, end = column_stack((x, ylow)), column_stack((x, yhigh))
                gc.line_set(start, end)
                axis = 0
                low = ylow
                high = yhigh

            else:
                y, xlow, xhigh = transpose(points)
                start, end = column_stack((xlow, y)), column_stack((xhigh, y))
                gc.line_set(start, end)
                axis = 1
                low = xlow
                high = xhigh

            if self.endcap_style == "bar":
                self._render_bar_endcap(gc, start, end, low, high, axis)
            else:
                gc.stroke_path()

        if not icon_mode:
            self._draw_default_axes(gc)
        return


    def _render_bar_endcap(self, gc, start, end, low, high, axis):
        """ Renders the endcaps for endcap_style == "bar".  start and end are
        the two endpoints of the bare errorbar.  axis is the column index
        corresponding to the index direction, so for orientation of 'h', axis
        is 0.

        This method modifies start and end.
        """
        delta = self.endcap_size / 2.0
        start[:,axis] -= delta
        end[:,axis] += delta

        start[:,1-axis] = low
        end[:,1-axis] = low
        gc.line_set(start, end)

        start[:,1-axis] = high
        end[:,1-axis] = high
        gc.line_set(start, end)
        gc.stroke_path()
        return


    def _render_icon(self, gc, x, y, width, height):
        pass
