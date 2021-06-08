#!/usr/bin/env python
"""
    Demonstrates usage of the TransformColorMapper class.
    - The colorbar is zoomable and panable.
"""

# Major library imports
from numpy import linspace, meshgrid, pi, cos, sin, log10

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import (
    HasTraits,
    Instance,
    Property,
    Float,
    Enum,
    Array,
    Tuple,
    Int,
    Callable,
    cached_property,
)
from traitsui.api import Item, UItem, HGroup, View, RangeEditor

# Chaco imports
from chaco.api import (
    ArrayPlotData,
    Plot,
    ColorBar,
    HPlotContainer,
    LinearMapper,
    LogMapper,
    CMapImagePlot,
    TransformColorMapper,
    viridis,
)
from chaco.tools.api import PanTool, ZoomTool


class DataGrid(HasTraits):
    """Holds a grid of 2D data that represents a function z = f(x,y)."""

    # ------------------------------------------------------
    # Primary Traits
    # ------------------------------------------------------

    # (xmin, ymin xmax, ymax)
    domain_bounds = Tuple(Float, Float, Float, Float)

    # grid dimensions: (Nx, Ny)
    grid_size = Tuple(Int, Int)

    # The function to evaluate on the grid.
    func = Callable

    # ------------------------------------------------------
    # Properties
    # ------------------------------------------------------

    # 1D array of x coordinates.
    x_array = Property(Array, observe=["domain_bounds, grid_size"])

    # 1D array of y coordinates.
    y_array = Property(Array, observe=["domain_bounds, grid_size"])

    # 2D array of function values, z = f(x,y)
    data = Property(Array, observe=["func, x_array, y_array"])

    data_min = Property(Float, observe=["data"])
    data_max = Property(Float, observe=["data"])

    # ------------------------------------------------------
    # Trait handlers
    # ------------------------------------------------------

    @cached_property
    def _get_x_array(self):
        xmin = self.domain_bounds[0]
        xmax = self.domain_bounds[2]
        nx = self.grid_size[0]
        x_array = linspace(xmin, xmax, nx)
        return x_array

    @cached_property
    def _get_y_array(self):
        ymin = self.domain_bounds[1]
        ymax = self.domain_bounds[3]
        ny = self.grid_size[1]
        y_array = linspace(ymin, ymax, ny)
        return y_array

    @cached_property
    def _get_data(self):
        # This might be called with func == None during initialization.
        if self.func is None:
            return None
        # Create a scalar field to colormap.
        xs = self.x_array
        ys = self.y_array
        x, y = meshgrid(xs, ys)
        z = self.func(x, y)[:-1, :-1]
        return z

    @cached_property
    def _get_data_min(self):
        return self.data.min()

    @cached_property
    def _get_data_max(self):
        return self.data.max()


def _create_plot_component(model):

    # Create a plot data object and give it the model's data array.
    pd = ArrayPlotData()
    pd.set_data("imagedata", model.data)

    # Create the "main" Plot.
    plot = Plot(pd, padding=50)

    # Use a TransformColorMapper for the color map.
    tcm = TransformColorMapper.from_color_map(viridis)

    # Create the image plot renderer in the main plot.
    renderer = plot.img_plot(
        "imagedata", xbounds=model.x_array, ybounds=model.y_array, colormap=tcm
    )[0]

    # Create the colorbar.
    lm = LinearMapper(
        range=renderer.value_range,
        domain_limits=(renderer.value_range.low, renderer.value_range.high),
    )
    colorbar = ColorBar(
        index_mapper=lm,
        plot=plot,
        orientation="v",
        resizable="v",
        width=30,
        padding=20,
    )

    colorbar.padding_top = plot.padding_top
    colorbar.padding_bottom = plot.padding_bottom

    # Add pan and zoom tools to the colorbar.
    colorbar.tools.append(
        PanTool(colorbar, constrain_direction="y", constrain=True)
    )
    zoom_overlay = ZoomTool(
        colorbar,
        axis="index",
        tool_mode="range",
        always_on=True,
        drag_button="right",
    )
    colorbar.overlays.append(zoom_overlay)

    # Create a container to position the plot and the colorbar side-by-side
    container = HPlotContainer(use_backbuffer=True)
    container.add(plot)
    container.add(colorbar)

    return container


class DataGridView(HasTraits):

    # The DataGrid instance plotted by this view.
    model = Instance(DataGrid)

    colormap_scale = Enum(
        "linear [default]",
        "log [data_func]",
        "power [data_func]",
        "power [unit_func]",
        "cos [unit_func]",
        "sin [unit_func]",
    )

    power = Float(1.0)

    colorbar_scale = Enum("linear", "log")

    plot = Instance(Component)

    img_renderer = Property(Instance(CMapImagePlot), observe=["plot"])

    colorbar = Property(Instance(ColorBar), observe=["plot"])

    traits_view = View(
        HGroup(
            Item("colormap_scale"),
            Item(
                "power",
                editor=RangeEditor(low=0.1, high=3.0, format="%4.2f"),
                visible_when='colormap_scale.startswith("power")',
                springy=True,
            ),
            Item("colorbar_scale"),
            springy=True,
        ),
        UItem("plot", editor=ComponentEditor()),
        width=750,
        height=500,
        resizable=True,
        title="TransformColorMapper Demo",
    )

    def _plot_default(self):
        return _create_plot_component(self.model)

    def _get_main_plot(self):
        return self.plot.components[0]

    def _get_img_renderer(self):
        return self.plot.components[0].components[0]

    def _get_colorbar(self):
        return self.plot.components[1]

    def _colormap_scale_changed(self):
        if self.colormap_scale == "linear [default]":
            self.img_renderer.color_mapper.data_func = None
            self.img_renderer.color_mapper.unit_func = None
        elif self.colormap_scale == "log [data_func]":
            self.img_renderer.color_mapper.data_func = log10
            self.img_renderer.color_mapper.unit_func = None
        elif self.colormap_scale == "power [data_func]":
            self.img_renderer.color_mapper.data_func = (
                lambda x: x ** self.power
            )
            self.img_renderer.color_mapper.unit_func = None
        elif self.colormap_scale == "power [unit_func]":
            self.img_renderer.color_mapper.data_func = None
            self.img_renderer.color_mapper.unit_func = (
                lambda x: x ** self.power
            )
        elif self.colormap_scale == "cos [unit_func]":
            self.img_renderer.color_mapper.data_func = None
            self.img_renderer.color_mapper.unit_func = lambda x: cos(
                0.5 * pi * x
            )
        elif self.colormap_scale == "sin [unit_func]":
            self.img_renderer.color_mapper.data_func = None
            self.img_renderer.color_mapper.unit_func = lambda x: sin(
                0.5 * pi * x
            )
        # FIXME: This call to request_redraw() should not be necessary.
        self.img_renderer.request_redraw()

    def _power_changed(self):
        if self.colormap_scale == "power [data_func]":
            self.img_renderer.color_mapper.data_func = (
                lambda x: x ** self.power
            )
        elif self.colormap_scale == "power [unit_func]":
            self.img_renderer.color_mapper.unit_func = (
                lambda x: x ** self.power
            )
        self.img_renderer.request_redraw()

    def _colorbar_scale_changed(self):
        rng = self.colorbar.index_mapper.range
        dlim = self.colorbar.index_mapper.domain_limits
        if self.colorbar_scale == "linear":
            new_mapper = LinearMapper(range=rng, domain_limits=dlim)
        else:  # 'log'
            new_mapper = LogMapper(range=rng, domain_limits=dlim)
        self.colorbar.index_mapper = new_mapper


grid = DataGrid(
    func=lambda x, y: 3.0 ** (x ** 2 + 2 * (cos(2 * pi * y) - 1)),
    domain_bounds=(0.0, 0.0, 2.0, 2.0),
    grid_size=(200, 200),
)
demo = DataGridView(model=grid)


if __name__ == "__main__":
    demo.configure_traits()
