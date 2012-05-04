from numpy import array, transpose, ndarray, empty
from traits.api import Instance, DelegatesTo, Bool, Int

from enable.api import transparent_color_trait
from chaco.color_mapper import ColorMapper
from chaco.base_xy_plot import BaseXYPlot
from chaco.linear_mapper import LinearMapper

class BandedMapper(LinearMapper):
    bands = Int(4)

    def map_screen(self, data_array):
        self._compute_scale()

        if self._null_data_range:
            if isinstance(data_array, (tuple, list, ndarray)):
                x = empty(data_array.shape)
                x.fill(self.low_pos)
                return x
            else:
                return array([self.low_pos])
        else:
            # Scale the data by the number of bands
            return (data_array*self.bands - self.range.low) * self._scale + self.low_pos

class HorizonPlot(BaseXYPlot):

    bands = DelegatesTo('value_mapper')
    color_mapper = Instance(ColorMapper)

    mirror = Bool(True)

    # Override parent traits

    orientation = 'h'

    def _color_mapper_changed(self, new):
        # change the number of steps to match the number of bands
        new.steps = self.bands*2+1

    def _gather_points(self):
        """ Collects the data points that are within the bounds of the plot and
        caches them.
        """
        if self._cache_valid:
            return

        index = self.index.get_data()
        value = self.value.get_data()

        if not self.index or not self.value:
            return

        if len(index) == 0 or len(value) == 0 or len(index) != len(value):
            self._cached_data_pts = []
            self._cache_valid = True
            return

        points = transpose(array((index,value)))
        self._cached_data_pts = points

        self._cache_valid = True

    def _render(self, gc, points):
        if len(points) == 0:
            return

        ox, oy = self.map_screen([[0,0]])[0]
        ylow, yhigh = self.value_mapper.screen_bounds

        y_plus_height = yhigh - oy

        # Get color bands
        bands = array(self.color_mapper._get_color_bands())

        with gc: 
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            # draw positive bands
            inc = -1 * array([0, y_plus_height])
            for i, col in enumerate(bands[self.bands+1:]):
                self._render_fill(gc, col, points+i*inc, ox, oy)

            # draw negative bands
            if self.mirror: 
                points[:,1] = oy - points[:,1]
                zeroy = oy
            else: 
                points[:,1] += y_plus_height
                inc *= -1
                zeroy = int(yhigh) + 2
            for i, col in enumerate(bands[self.bands-1::-1]):
                self._render_fill(gc, col, points+i*inc, ox, zeroy)

    def _render_fill(self, gc, face_col, points, ox, oy):
        gc.set_fill_color(face_col)
        gc.begin_path()
        startx, starty = points[0]
        gc.move_to(startx, oy) 
        gc.line_to(startx, starty)

        gc.lines(points)

        endx, endy = points[-1]
        gc.line_to(endx, oy) 
        gc.line_to(startx, oy) 

        gc.close_path()
        gc.fill_path()
