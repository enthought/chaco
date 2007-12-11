""" A Plot which uses ScaleSystems for its ticks.
"""

from enthought.traits.api import Any

from enthought.chaco2.api import (DataRange2D, LinearMapper, LogMapper,
    PlotGrid, Plot)
from enthought.chaco2.scales_axis import PlotAxis
from enthought.chaco2.scales_tick_generator import ScalesTickGenerator
from enthought.chaco2.scales.api import DefaultScale, LogScale, ScaleSystem


def add_default_axes(plot, orientation="normal", vtitle="", htitle=""):
    """
    Creates left and bottom axes for a plot.  Assumes that the index is
    horizontal and value is vertical by default; set orientation to
    something other than "normal" if they are flipped.
    """
    if orientation in ("normal", "h"):
        v_mapper = plot.value_mapper
        h_mapper = plot.index_mapper
    else:
        v_mapper = plot.index_mapper
        h_mapper = plot.value_mapper
    
    yticks = ScalesTickGenerator()
    left = PlotAxis(
        orientation='left',
        title=vtitle,
        mapper=v_mapper,
        component=plot,
        tick_generator=yticks,
    )
    
    xticks = ScalesTickGenerator()
    bottom = PlotAxis(
        orientation='bottom',
        title=htitle,
        mapper=h_mapper,
        component=plot,
        tick_generator=xticks,
    )

    plot.underlays.append(left)
    plot.underlays.append(bottom)
    return left, bottom


class ScalyPlot(Plot):
    x_axis = Any()
    y_axis = Any()
    x_ticks = Any()
    y_ticks = Any()
    linear_scale = Any()
    log_scale = Any()

    def _linear_scale_default(self):
        return ScaleSystem(DefaultScale())

    def _log_scale_default(self):
        return ScaleSystem(LogScale())

    def _init_components(self):
        # Since this is called after the HasTraits constructor, we have to make
        # sure that we don't blow away any components that the caller may have
        # already set.

        if self.range2d is None:
            self.range2d = DataRange2D()

        if self.index_mapper is None:
            if self.index_scale == "linear":
                imap = LinearMapper(range=self.range2d.x_range)
            else:
                imap = LogMapper(range=self.range2d.x_range)
            self.index_mapper = imap
        
        if self.value_mapper is None:
            if self.value_scale == "linear":
                vmap = LinearMapper(range=self.range2d.y_range)
            else:
                vmap = LogMapper(range=self.range2d.y_range)
            self.value_mapper = vmap

        if self.x_ticks is None:
            scale = dict(linear=self.linear_scale, log=self.log_scale).get(
                self.index_scale, self.linear_scale)
            self.x_ticks = ScalesTickGenerator(scale=scale)
        if self.y_ticks is None:
            scale = dict(linear=self.linear_scale, log=self.log_scale).get(
                self.value_scale, self.linear_scale)
            self.y_ticks = ScalesTickGenerator(scale=scale)

        if self.x_grid is None:
            self.x_grid = PlotGrid(mapper=self.x_mapper, orientation="vertical",
                                  line_color="lightgray", line_style="dot",
                                  component=self, tick_generator=self.x_ticks)
        if self.y_grid is None:
            self.y_grid = PlotGrid(mapper=self.y_mapper, orientation="horizontal",
                                  line_color="lightgray", line_style="dot",
                                  component=self, tick_generator=self.y_ticks)
        if self.x_axis is None:
            self.x_axis = PlotAxis(mapper=self.x_mapper, orientation="bottom",
                                  component=self, tick_generator=self.x_ticks)
        if self.y_axis is None:
            self.y_axis = PlotAxis(mapper=self.y_mapper, orientation="left",
                                  component=self, tick_generator=self.y_ticks)

    def _index_scale_changed(self, old, new):
        Plot._index_scale_changed(self, old, new)
        # Now adjust the ScaleSystems.
        scale = dict(linear=self.linear_scale, log=self.log_scale).get(
            self.index_scale, self.linear_scale)
        self.x_ticks.scale = scale

    def _value_scale_changed(self, old, new):
        Plot._value_scale_changed(self, old, new)
        scale = dict(linear=self.linear_scale, log=self.log_scale).get(
            self.value_scale, self.linear_scale)
        self.y_ticks.scale = scale
