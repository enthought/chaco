""" A Plot which uses ScaleSystems for its ticks.
"""

from traits.api import Any

from chaco.axis import PlotAxis
from chaco.data_range_2d import DataRange2D
from chaco.grid import PlotGrid
from chaco.linear_mapper import LinearMapper
from chaco.log_mapper import LogMapper
from chaco.plot import Plot
from chaco.scales.scales import DefaultScale, LogScale, ScaleSystem
from chaco.scales_tick_generator import ScalesTickGenerator


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
        orientation="left",
        title=vtitle,
        mapper=v_mapper,
        component=plot,
        tick_generator=yticks,
    )

    xticks = ScalesTickGenerator()
    bottom = PlotAxis(
        orientation="bottom",
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
    linear_scale_factory = Any()
    log_scale_factory = Any()

    def _linear_scale_default(self):
        return self._make_scale("linear")

    def _log_scale_default(self):
        return self._make_scale("log")

    def _make_scale(self, scale_type="linear"):
        """ Returns a new linear or log scale """
        if scale_type == "linear":
            if self.linear_scale_factory is not None:
                return self.linear_scale_factory()
            else:
                return ScaleSystem(DefaultScale())
        else:
            if self.log_scale_factory is not None:
                return self.log_scale_factory()
            else:
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
            self.x_ticks = ScalesTickGenerator(
                scale=self._make_scale(self.index_scale)
            )
        if self.y_ticks is None:
            self.y_ticks = ScalesTickGenerator(
                scale=self._make_scale(self.value_scale)
            )

        if self.x_grid is None:
            self.x_grid = PlotGrid(
                mapper=self.x_mapper,
                orientation="vertical",
                line_color="lightgray",
                line_style="dot",
                component=self,
                tick_generator=self.x_ticks,
            )
        if self.y_grid is None:
            self.y_grid = PlotGrid(
                mapper=self.y_mapper,
                orientation="horizontal",
                line_color="lightgray",
                line_style="dot",
                component=self,
                tick_generator=self.y_ticks,
            )
        if self.x_axis is None:
            self.x_axis = PlotAxis(
                mapper=self.x_mapper,
                orientation="bottom",
                component=self,
                tick_generator=self.x_ticks,
            )
        if self.y_axis is None:
            self.y_axis = PlotAxis(
                mapper=self.y_mapper,
                orientation="left",
                component=self,
                tick_generator=self.y_ticks,
            )

    def _index_scale_changed(self, old, new):
        Plot._index_scale_changed(self, old, new)
        # Now adjust the ScaleSystems.
        self.x_ticks.scale = self._make_scale(self.index_scale)

    def _value_scale_changed(self, old, new):
        Plot._value_scale_changed(self, old, new)
        # Now adjust the ScaleSystems.
        self.y_ticks.scale = self._make_scale(self.value_scale)
