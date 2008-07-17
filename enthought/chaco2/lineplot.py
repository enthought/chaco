""" Defines the LinePlot class.
"""

# Standard library imports
import warnings

# Major library imports
from numpy import argsort, array, concatenate, inf, invert, isnan, \
                  take, transpose, zeros

# Enthought library imports
from enthought.enable2.api import black_color_trait, ColorTrait, LineStyle
from enthought.traits.api import Enum, Float, List, Str
from enthought.traits.ui.api import Item, View

# Local relative imports
from base import arg_find_runs, bin_search, reverse_map_1d
from base_xy_plot import BaseXYPlot



class LinePlot(BaseXYPlot):
    """ A plot consisting of a line.
    
    This is the most fundamental object to use to create line plots. However,
    it is somewhat low-level and therefore creating one properly to do what
    you want can require some verbose code. The create_line_plot() function
    in plot_factory.py can hide some of this verbosity for common cases.
    """
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
    #   connectedpoints - "normal" style (default); each point is connected to
    #       subsequent and prior points by line segments
    #   hold - each point is represented by a line segment parallel to the
    #       abscissa (index axis) and spanning the length between the point
    #       and its subsequent point.
    #   connectedhold - like "hold" style, but line segments are drawn at
    #       each point of the plot to connect the hold lines of the prior
    #       point and the current point.  Also called a "right angle plot".
    render_style = Enum("connectedpoints", "hold", "connectedhold")

    # Traits UI View for customizing the plot.
    traits_view = View(Item("color", style="custom"), "line_width", "line_style",
                       buttons=["OK", "Cancel"])

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    # Cached list of non-NaN arrays of (x,y) data-space points; regardless of
    # self.orientation, this is always stored as (index_pt, value_pt).  This is
    # different from the default BaseXYPlot definition.
    _cached_data_pts = List

    # Cached list of non-NaN arrays of (x,y) screen-space points.
    _cached_screen_pts = List


    def hittest(self, screen_pt, threshold=7.0):
        """
        Tests whether the given screen point is within *threshold* pixels of 
        any data points on the line.  If so, then it returns the (x,y) value of
        a data point near the screen point.  If not, then it returns None.

        Note: This only checks data points and *not* the actual line segments
        connecting them.
        """
        ndx = self.map_index(screen_pt, threshold)
        if ndx is not None:
            return (self.index.get_data()[ndx], self.value.get_data()[ndx])
        else:
            data_x = self.map_data(screen_pt)
            xmin, xmax = self.index.get_bounds()
            if xmin <= data_x <= xmax:
                if self.orientation == "h":
                    sy = screen_pt[1]
                else:
                    sy = screen_pt[0]
            
                interp_val = self.interpolate(data_x)
                interp_y = self.value_mapper.map_screen(interp_val)
                
                if abs(sy - interp_y) <= threshold:
                    return reverse_map_1d(self.index.get_data(), data_x,
                                          self.index.sort_order)
            return None

    def interpolate(self, index_value):
        """
        Returns the value of the plot at the given index value in screen space.
        Raises an IndexError when *index_value* exceeds the bounds of indexes on
        the value.
        """

        if self.index is None or self.value is None:
            raise IndexError, "cannot index when data source index or value is None"

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
            slope = float(y1 - y0)/float(x1 - x0)
            dx = index_value - x0
            yp = y0 + slope * dx
        else:
            yp = inf

        return yp

    def get_screen_points(self):
        self._gather_points()
        return [self.map_screen(ary) for ary in self._cached_data_pts]

    #------------------------------------------------------------------------
    # Private methods; implements the BaseXYPlot stub methods
    #------------------------------------------------------------------------

    def _gather_points(self):
        """
        Collects the data points that are within the bounds of the plot and 
        caches them.
        """
        if not self._cache_valid:

            if not self.index or not self.value:
                return

            index = self.index.get_data()
            value = self.value.get_data()

            # Check to see if the data is completely outside the view region
            for ds, rng in ((self.index, self.index_range), (self.value, self.value_range)):
                low, high = ds.get_bounds()
                if low > rng.high or high < rng.low:
                    return

            if len(index) == 0 or len(value) == 0 or len(index) != len(value):
                self._cached_data_pts = []
                self._cache_valid = True

            size_diff = len(value) - len(index)
            if size_diff > 0:
                warnings.warn('Chaco2.LinePlot: len(value) %d - len(index) %d = %d\n' \
                              % (len(value), len(index), size_diff))
                index_max = len(index)
                value = value[:index_max]
            else:
                index_max = len(value)
                index = index[:index_max]

            # TODO: restore the functionality of rendering highlighted portions 
            # of the line
            #selection = self.index.metadata.get(self.metadata_name, None) 
            #if selection is not None and type(selection) in (ndarray, list) and \
            #        len(selection) > 0:

            # Split the index and value raw data into non-NaN chunks
            nan_mask = invert(isnan(value)) & invert(isnan(index))
            blocks = [b for b in arg_find_runs(nan_mask, "flat") if nan_mask[b[0]] != 0]

            points = []
            for block in blocks:
                start, end = block
                block_index = index[start:end]
                block_value = value[start:end]
                index_mask = self.index_mapper.range.mask_data(block_index)

                runs = [r for r in arg_find_runs(index_mask, "flat") \
                        if index_mask[r[0]] != 0]

                # Check to see if our data view region is between two points in the
                # index data.  If so, then we have to reverse map our current view
                # into the appropriate index and draw the bracketing points.
                if runs == []:
                    data_pt = self.map_data((self.x_mapper.low_pos, self.y_mapper.low_pos))
                    if self.index.sort_order == "none":
                        indices = argsort(index)
                        sorted_index = take(index, indices)
                        sorted_value = take(value, indices)
                        sort = 1
                    else:
                        sorted_index = index
                        sorted_value = value
                        if self.index.sort_order == "ascending":
                            sort = 1
                        else:
                            sort = -1
                    ndx = bin_search(sorted_index, data_pt, sort)
                    if ndx == -1:
                        # bin_search can return -1 if data_pt is outside the bounds
                        # of the source data
                        continue

                    points.append(transpose(array((sorted_index[ndx:ndx+2],
                                                   sorted_value[ndx:ndx+2]))))

                else:
                    # Expand the width of every group of points so we draw the lines
                    # up to their next point, outside the plot area
                    data_end = len(index_mask)
                    for run in runs:
                        start, end = run
                        if start != 0:
                            start -= 1
                        if end != data_end:
                            end += 1

                        run_data = transpose(array((block_index[start:end],
                                                    block_value[start:end])))
                        points.append(run_data)

            self._cached_data_pts = points
            self._cache_valid = True
        return

    def _downsample(self):
        if not self._screen_cache_valid:
            self._cached_screen_pts = [self.map_screen(p) for p in self._cached_data_pts]
            self._screen_cache_valid = True

            pt_arrays = self._cached_screen_pts

            # some boneheaded short-circuits
            m = self.index_mapper
            total_numpoints = sum([p.shape for p in pt_arrays])
            if (total_numpoints < 400) or (total_numpoints < m.high_pos - m.low_pos):
                return self._cached_screen_pts

            # the new point array and a counter of how many actual points we've added
            # to it
            new_arrays = []
            for pts in pt_arrays:
                new_pts = zeros(pts.shape, "d")
                numpoints = 1
                new_pts[0] = pts[0]

                last_x, last_y = pts[0]
                for x, y in pts[1:]:
                    if (x-last_x)**2 + (y-last_y)**2 > 2:
                        new_pts[numpoints] = (x,y)
                        last_x = x
                        last_y = y
                        numpoints += 1

                new_arrays.append(new_pts[:numpoints])
        return self._cached_screen_pts

    def _render(self, gc, points, selected_points=None):
        if len(points) == 0:
            return

        gc.save_state()
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
            render(gc, selected_points)

        # Render using the normal style
        gc.set_stroke_color(self.color_)
        gc.set_line_width(self.line_width)
        gc.set_line_dash(self.line_style_)
        render(gc, points)

        # Draw the default axes, if necessary
        self._draw_default_axes(gc)

        gc.restore_state()

    def _render_normal(self, gc, points):
        for ary in points:
            if len(ary) > 0:
                gc.begin_path()
                gc.lines(ary)
                gc.stroke_path()
        return

    def _render_hold(self, gc, points):
        for starts in points:
            x,y = starts.T
            ends = transpose(array( (x[1:], y[:-1]) ))
            gc.begin_path()
            gc.line_set(starts[:-1], ends)
            gc.stroke_path()
        return

    def _render_connected_hold(self, gc, points):
        for starts in points:
            x,y = starts.T
            ends = transpose(array( (x[1:], y[:-1]) ))
            gc.begin_path()
            gc.line_set(starts[:-1], ends)
            gc.line_set(ends, starts[1:])
            gc.stroke_path()
        return

    def _render_icon(self, gc, x, y, width, height):
        gc.save_state()
        gc.set_stroke_color(self.color_)
        gc.set_line_width(self.line_width)
        gc.set_line_dash(self.line_style_)
        gc.set_antialias(0)
        gc.move_to(x, y+height/2)
        gc.line_to(x+width, y+height/2)
        gc.stroke_path()
        gc.restore_state()
        return

    def _downsample_vectorized(self):
        """
        Analyzes the screen-space points stored in self._cached_data_pts
        and replaces them with a downsampled set.
        """
        pts = self._cached_screen_pts  #.astype(int)

        # some boneheaded short-circuits
        m = self.index_mapper
        if (pts.shape[0] < 400) or (pts.shape[0] < m.high_pos - m.low_pos):
            return

        pts2 = concatenate((array([[0.0,0.0]]), pts[:-1]))
        z = abs(pts - pts2)
        d = z[:,0] + z[:,1]
        #... TODO ...
        return

    def _color_changed(self):
        self.invalidate_draw()
        self.request_redraw()
        return

    def _line_style_changed(self):
        self.invalidate_draw()
        self.request_redraw()
        return

    def _line_width_changed(self):
        self.invalidate_draw()
        self.request_redraw()
        return

    def __getstate__(self):
        state = super(LinePlot,self).__getstate__()
        for key in ['traits_view']:
            if state.has_key(key):
                del state[key]

        return state


# EOF
