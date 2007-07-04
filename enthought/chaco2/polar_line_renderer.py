
# Major library imports
from numpy import add, arange, array, compress, concatenate, cos, pi, sin, transpose, zeros

# Enthought library imports
from enthought.enable2.api import black_color_trait, LineStyle
from enthought.traits.api import Any, Float, Int, Str, Trait, Unicode, \
                                 Bool, Event, List, Array, Instance, Enum, false, true

# Local, relative imports
from abstract_plot_renderer import AbstractPlotRenderer
from array_data_source import ArrayDataSource
from base import reverse_map_1d
from base_xy_plot import BaseXYPlot
from label import Label
import ticks

class PolarLineRenderer(AbstractPlotRenderer):

    #------------------------------------------------------------------------
    # Appearance-related traits
    #------------------------------------------------------------------------
    origin_axis_color_ = (0,0,0,1)
    origin_axis_width = 2.0
    origin_axis_visible=True
    grid_visible= True
    orientation = 'h'
    color = black_color_trait
    line_width = Float(1.0)
    line_style = LineStyle("solid")
    grid_style= LineStyle("dot")

    def _gather_points(self):
        # This is just a stub for now.  We should really find the lines only
        # inside the screen range here.

        x = self.index.get_data()
        y = self.value.get_data()
        rad= min(self.width/2.0,self.height/2.0)
        sx = x*rad+ self.x + self.width/2.0
        sy = y*rad+ self.y + self.height/2.0

        points = transpose(array((sx,sy)))
        self._cached_data_pts = points
        self._cache_valid = True
        return

    def _data_changed(self):
        self._cache_valid = False
        return

    def _update_mappers(self):
        #Dunno if there is anything else to do here
        self._cache_valid = False

    def _render(self, gc, points):
        gc.save_state()

        gc.set_antialias(True)
        self._draw_default_axes(gc)
        self._draw_default_grid(gc)
        if len(points)>0:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            gc.set_stroke_color(self.color_)
            gc.set_line_width(self.line_width)
            gc.set_line_dash(self.line_style_)

            gc.begin_path()
            gc.lines(points)
            gc.stroke_path()

        gc.restore_state()

        return

    def map_screen(self, data_array):

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

        if self.orientation == 'h':
            return transpose(array((sx, sy)))
        else:
            return transpose(array((sy, sx)))

    def map_data(self, screen_pt):
        if self.orientation == 'h':
            x, y = screen_pt
        else:
            y,x = screen_pt
        return array((self.index_mapper.map_data(x),
                      self.value_mapper.map_data(y)))


    def _downsample(self):
        return self.map_screen(self._cached_data_pts)

    def _draw_plot(self, *args, **kw):
        "Simple compatibility with new-style rendering loop"
        return self._draw_component(*args, **kw)


    def _draw_component(self, gc, view_bounds=None, mode='normal'):
        self._gather_points()
        self._render(gc, self._cached_data_pts)

    def _bounds_changed(self):
        self._update_mappers()
        return

    def _bounds_items_changed(self):
        self._update_mappers()
        return

    def _draw_default_axes(self, gc):
        if not self.origin_axis_visible:
            return
        gc.save_state()
        gc.set_stroke_color(self.origin_axis_color_)
        gc.set_line_width(self.origin_axis_width)
        gc.set_line_dash(self.grid_style_)
        x_data,y_data= transpose(self._cached_data_pts)
        x_center=self.x + self.width/2.0
        y_center=self.y + self.height/2.0

        for theta in range(12):
                r= min(self.width/2.0,self.height/2.0)
                x= r*cos(theta*pi/6) + x_center
                y= r*sin(theta*pi/6) + y_center
                data_pts= array([[x_center,y_center],[x,y]])
                start,end = data_pts
                gc.move_to(int(start[0]), int(start[1]))
                gc.line_to(int(end[0]), int(end[1]))
                gc.stroke_path()
        gc.restore_state()
        return

    def _draw_default_grid(self,gc):
        if not self.grid_visible:
            return
        gc.save_state()
        gc.set_stroke_color(self.origin_axis_color_)
        gc.set_line_width(self.origin_axis_width)
        gc.set_line_dash(self.grid_style_)
        x_data,y_data= transpose(self._cached_data_pts)
        x_center=self.x + self.width/2.0
        y_center=self.y + self.height/2.0
        for r_part in range(5):
            rad= min(self.width/2.0,self.height/2.0)
            r= rad*r_part/4
            gc.move_to(self.x,self.y)
            gc.arc(x_center,y_center,r,0,2*pi)
            gc.stroke_path()

        gc.restore_state()
        return

# EOF
