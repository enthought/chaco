
# Major library imports
from numpy import any, argsort, array, compress, concatenate, invert, isnan, \
                  take, transpose, zeros

# Enthought library imports
from enthought.enable2.api import black_color_trait, ColorTrait, LineStyle
from enthought.traits.api import Float, List
from enthought.traits.ui.api import Item, View
from enthought.logger import logger

# Local relative imports
from base import arg_find_runs, bin_search
from base_xy_plot import BaseXYPlot


class LinePlot(BaseXYPlot):
    
    # The color of the line
    color = black_color_trait

    # The color to use to highlight line when selected
    selected_color = ColorTrait("lightyellow")

    # The style of the selected line
    selected_line_style = LineStyle("solid")
    
    # The thickness of the line
    line_width = Float(1.0)
    
    # The line dash style
    line_style = LineStyle

    # Traits UI View
    traits_view = View(Item("color", style="custom"), "line_width", "line_style", 
                       buttons=["OK", "Cancel"])

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # List of non-NaN arrays of (x,y) data-space points; regardless of
    # self.orientation, this is always stored (index_pt, value_pt).  This is
    # different from the default BaseXYPlot definition.
    _cached_data_pts = List
    
    # List of non-NaN arrays of (x,y) screen space points
    _cached_screen_pts = List


    
    def hittest(self, screen_pt, threshold=7.0):
        """
        Returns if the given screen point is within threshold of any data points
        on the line.  If so, then returns the (x,y) value of a datapoint near
        the screen point.  If not, then returns None.
        
        Note: This only checks data points and *not* the actual line segments
              connecting them.
        """
        # TODO: implement point-line distance computation so this method isn't
        #       quite so limited!
        ndx = self.map_index(screen_pt, threshold)
        if ndx is not None:
            return (self.index.get_data()[ndx], self.value.get_data()[ndx])
        else:
            return None

    def interpolate(self, index_value):
        """
        Returns the value of the plot at the given index value in screen
        space.
        Raises IndexError when index_value exeeds the bounds of indexes on value.
        """

        if self.index is None or self.value is None:
            raise IndexError, "cannot index when data source index or value is None"
        
        index_data = self.index.get_data()
        value_data = self.value.get_data()
        
        from base import reverse_map_1d
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

        return yp

    def get_screen_points(self):
        self._gather_points()
        return [self.map_screen(ary) for ary in self._cached_data_pts]

    #------------------------------------------------------------------------
    # Private methods; implements the BaseXYPlot stub methods
    #------------------------------------------------------------------------

    def _gather_points(self):
        """
        Gathers up the data points that are within our bounds and stores them
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
                logger.warn("Chaco2: using empty dataset; index_len=%d, value_len=%d." \
                                    % (len(index), len(value)))
                self._cached_data_pts = []
                self._cache_valid = True

            size_diff = len(value) - len(index)
            if size_diff > 0:
                print 'WARNING lineplot._gather_points: len(value)', len(value), \
                      '- len(index)', len(index), '=', size_diff, '\n'
                index_max = len(index)
                value = value[:index_max]
            else:
                index_max = len(value)
                index = index[:index_max]

            # Split the index and value raw data into non-NaN chunks
            nan_mask = invert(isnan(value)) & invert(isnan(index))
            blocks = [b for b in arg_find_runs(nan_mask, "flat") if nan_mask[b[0]] != 0]

            points = []
            for block in blocks:
                start, end = block  # obviated by fancy indexing in numpy
                block_index = index[start:end]
                block_value = value[start:end]
                index_mask = self.index_mapper.range.mask_data(block_index)
                value_mask = self.value_mapper.range.mask_data(block_value)
                
                # Optimization: see if we can clip out extraneous values; if
                # this leads to an empty mask, then just use the index mask
                # to be safe.
                point_mask = index_mask & value_mask
                if not any(point_mask):
                    point_mask = index_mask
                
                runs = [r for r in arg_find_runs(point_mask, "flat") \
                        if point_mask[r[0]] != 0]
                
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
                    data_end = len(point_mask)
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

    def _render(self, gc, points):
        if len(points) == 0:
            return

        gc.save_state()
        gc.set_antialias(True)

        gc.clip_to_rect(self.x, self.y, self.width, self.height)

        if self.index.metadata.get('selections') is not None:
            if type(self.index.metadata['selections']) in (array, list) and \
                                len(self.index.metadata['selections']) > 0:
                # TODO: use mask in metadata to select certain regions
                # for now, assume whole line is selected
                gc.set_stroke_color(self.selected_color_)
                gc.set_line_width(self.line_width+10.0)
                gc.set_line_dash(self.selected_line_style_)
            
                for ary in points:
                    if len(ary) > 0:
                        gc.begin_path()
                        gc.lines(ary)
                        gc.stroke_path()

        gc.set_stroke_color(self.color_)
        gc.set_line_width(self.line_width)
        gc.set_line_dash(self.line_style_)

        for ary in points:
            if len(ary) > 0:
                gc.begin_path()
                gc.lines(ary)
                gc.stroke_path()
        
        # Draw the default axes, if necessary
        self._draw_default_axes(gc)
        
        gc.restore_state()
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
        Does an analysis on the screen-space points stored in self._cached_data_pts
        and replaces it with a downsampled version.
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
