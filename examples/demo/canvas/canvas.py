#!/usr/bin/env python
"""
The main app for the PlotCanvas application
"""

# FIXME - this is broken

MULTITOUCH = False
DEBUG = False

# Major library imports
from copy import copy
from numpy import arange, fabs, linspace, pi, sin
from numpy import random
from scipy.special import jn


# Enthought library imports
from enable.api import Viewport, Window
from enable.tools.api import MoveTool, ResizeTool, ViewportPanTool
from enable.example_support import DemoFrame, demo_main
from traits.api import Any, Bool, Enum, Float, HasTraits, Instance, List, Str


# Chaco imports
from chaco.api import (
    AbstractOverlay,
    ArrayPlotData,
    Plot,
    ScatterPlot,
    LinePlot,
    LinearMapper,
)
from chaco.tools.api import PanTool, ZoomTool, LegendTool

# Canvas imports
from chaco.plot_canvas import PlotCanvas
from chaco.plot_canvas_toolbar import PlotCanvasToolbar, PlotToolbarButton
from transient_plot_overlay import TransientPlotOverlay
from axis_tool import AxisTool, RangeController, MPAxisTool
from plot_clone_tool import PlotCloneTool, MPPlotCloneTool
from data_source_button import ButtonController, DataSourceButton
from mp_move_tool import MPMoveTool
from mp_viewport_pan_tool import MPViewportPanTool

# from canvas_grid import CanvasGrid

# Multitouch imports
if MULTITOUCH:
    from mptools import (
        MPPanTool,
        MPDragZoom,
        MPLegendTool,
        MPPanZoom,
        MPRangeSelection,
    )

    # AxisTool = MPAxisTool
    PlotCloneTool = MPPlotCloneTool

NUMPOINTS = 250
DATA = {
    "GOOG": random.uniform(-2.0, 10.0, NUMPOINTS),
    "MSFT": random.uniform(-2.0, 10.0, NUMPOINTS),
    "AAPL": random.uniform(-2.0, 10.0, NUMPOINTS),
    "YHOO": random.uniform(-2.0, 10.0, NUMPOINTS),
    "CSCO": random.uniform(-2.0, 10.0, NUMPOINTS),
    "INTC": random.uniform(-2.0, 10.0, NUMPOINTS),
    "ORCL": random.uniform(-2.0, 10.0, NUMPOINTS),
    "HPQ": random.uniform(-2.0, 10.0, NUMPOINTS),
    "DELL": random.uniform(-2.0, 10.0, NUMPOINTS),
}


def add_basic_tools(plot):
    plot.tools.append(PanTool(plot))
    plot.tools.append(MoveTool(plot, drag_button="right"))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)


def do_plot(name, pd):
    xname = name + "_x"
    yname = name + "_y"
    pd.set_data(xname, list(range(len(DATA[name]))))
    pd.set_data(yname, DATA[name])

    plot = Plot(
        pd,
        padding=30,
        unified_draw=True,
        border_visible=True,
    )
    plot.x_axis.visible = False
    plot.title = name
    plot.plot(
        (xname, yname),
        name=name,
        type="line",
        color="blue",
    )
    return plot


def clone_renderer(r):
    """ Returns a clone of plot renderer r """
    basic_traits = [
        "orientation",
        "line_width",
        "color",
        "outline_color",
        "bgcolor",
        "border_visible",
        "border_color",
        "visible",
        "fill_padding",
        "resizable",
        "aspect_ratio",
        "draw_layer",
        "draw_order",
        "border_width",
        "resizable",
        "index",
        "value",
    ]

    scatter_traits = [
        "custom_symbol",
        "marker",
        "marker_size",
        "selection_marker",
        "selection_marker_size",
        "selection_line_width",
        "selection_color",
    ]

    line_traits = [
        "selected_color",
        "selected_line_style",
        "metadata_name",
        "render_style",
    ]

    if isinstance(r, ScatterPlot):
        return r.clone_traits(basic_traits + scatter_traits)
    elif isinstance(r, LinePlot):
        return r.clone_traits(basic_traits + line_traits)


def clone_plot(clonetool, drop_position):
    # A little sketchy...
    canvas = clonetool.component.container.component.component

    # Create a new Plot object
    oldplot = clonetool.component
    newplot = Plot(oldplot.data)
    basic_traits = [
        "orientation",
        "default_origin",
        "bgcolor",
        "border_color",
        "border_width",
        "border_visible",
        "draw_layer",
        "unified_draw",
        "fit_components",
        "fill_padding",
        "visible",
        "aspect_ratio",
        "title",
    ]

    for attr in basic_traits:
        setattr(newplot, attr, getattr(oldplot, attr))

    # copy the ranges
    dst = newplot.range2d
    src = oldplot.range2d
    # for attr in ('_low_setting', '_low_value', '_high_setting', '_high_value'):
    #    setattr(dst, attr, getattr(src, attr))
    dst._xrange.sources = copy(src._xrange.sources)
    dst._yrange.sources = copy(src._yrange.sources)

    newplot.padding = oldplot.padding
    newplot.bounds = oldplot.bounds[:]
    newplot.resizable = ""
    newplot.position = drop_position

    newplot.datasources = copy(oldplot.datasources)

    for name, renderers in list(oldplot.plots.items()):
        newrenderers = []
        for renderer in renderers:
            new_r = clone_renderer(renderer)
            new_r.index_mapper = LinearMapper(range=newplot.index_range)
            new_r.value_mapper = LinearMapper(range=newplot.value_range)
            new_r._layout_needed = True
            new_r.invalidate_draw()
            new_r.resizable = "hv"
            newrenderers.append(new_r)
        newplot.plots[name] = newrenderers
    # newplot.plots = copy(oldplot.plots)

    for name, renderers in list(newplot.plots.items()):
        newplot.add(*renderers)

    newplot.index_axis.title = oldplot.index_axis.title
    newplot.index_axis.unified_draw = True
    newplot.value_axis.title = oldplot.value_axis.title
    newplot.value_axis.unified_draw = True

    # Add new tools to the new plot
    newplot.tools.append(
        AxisTool(component=newplot, range_controller=canvas.range_controller)
    )

    # Add tools to the new plot
    pan_traits = [
        "drag_button",
        "constrain",
        "constrain_key",
        "constrain_direction",
        "speed",
    ]
    zoom_traits = [
        "tool_mode",
        "always_on",
        "axis",
        "enable_wheel",
        "drag_button",
        "wheel_zoom_step",
        "enter_zoom_key",
        "exit_zoom_key",
        "pointer",
        "color",
        "alpha",
        "border_color",
        "border_size",
        "disable_on_complete",
        "minimum_screen_delta",
        "max_zoom_in_factor",
        "max_zoom_out_factor",
    ]
    move_traits = [
        "drag_button",
        "end_drag_on_leave",
        "cancel_keys",
        "capture_mouse",
        "modifier_key",
    ]

    if not MULTITOUCH:
        for tool in oldplot.tools:
            if isinstance(tool, PanTool):
                newtool = tool.clone_traits(pan_traits)
                newtool.component = newplot
                break
        else:
            newtool = PanTool(newplot)
        # Reconfigure the pan tool to always use the left mouse, because we will
        # put plot move on the right mouse button
        newtool.drag_button = "left"
        newplot.tools.append(newtool)

        for tool in oldplot.tools:
            if isinstance(tool, MoveTool):
                newtool = tool.clone_traits(move_traits)
                newtool.component = newplot
                break
        else:
            newtool = MoveTool(newplot, drag_button="right")
        newplot.tools.append(newtool)

        for tool in oldplot.tools:
            if isinstance(tool, ZoomTool):
                newtool = tool.clone_traits(zoom_traits)
                newtool.component = newplot
                break
        else:
            newtool = ZoomTool(newplot)
        newplot.tools.append(newtool)

    else:
        pz = MPPanZoom(newplot)
        # pz.pan.constrain = True
        # pz.pan.constrain_direction = "x"
        # pz.zoom.mode = "range"
        # pz.zoom.axis = "index"
        newplot.tools.append(MPPanZoom(newplot))
        # newplot.tools.append(MTMoveTool(

    newplot._layout_needed = True

    clonetool.dest.add(newplot)
    newplot.invalidate_draw()
    newplot.request_redraw()
    canvas.request_redraw()


def make_toolbar(canvas):
    # Create the toolbar
    toolbar = PlotCanvasToolbar(
        bounds=[70, 200],
        position=[50, 350],
        fill_padding=True,
        bgcolor="lightgrey",
        padding=5,
        align="left",
    )

    # Create the scatterplot
    pd = ArrayPlotData()
    scatterplot = Plot(
        pd, padding=15, bgcolor="white", unified_draw=True, border_visible=True
    )
    if not MULTITOUCH:
        scatterplot.tools.append(PanTool(scatterplot, drag_button="right"))
        scatterplot.tools.append(ZoomTool(scatterplot))
    else:
        scatterplot.tools.append(MPPanZoom(scatterplot))
    scatterplot.overlays.append(
        PlotCloneTool(scatterplot, dest=canvas, plot_cloner=clone_plot)
    )

    # Create the overlay
    overlay = TransientPlotOverlay(
        component=toolbar,
        overlay_component=scatterplot,
        bounds=[350, 350],
        border_visible=True,
        visible=False,  # initially invisible
    )
    scatterplot.container = overlay

    # Create buttons
    controller = ButtonController()
    for name in list(DATA.keys()):
        plot = do_plot(name, pd)
        if MULTITOUCH:
            plot.tools.append(MPPanZoom(plot))
        else:
            plot.tools.append(
                PanTool(
                    plot,
                    drag_button="right",
                    constrain=True,
                    constrain_direction="x",
                )
            )
            plot.tools.append(
                ZoomTool(
                    plot, tool_mode="range", axis="index", always_on=False
                )
            )
        plot.overlays.append(
            PlotCloneTool(plot, dest=canvas, plot_cloner=clone_plot)
        )
        plot_overlay = TransientPlotOverlay(
            component=toolbar,
            overlay_component=plot,
            border_visible=True,
            visible=False,
        )
        plot.container = plot_overlay
        button = DataSourceButton(
            label=name,
            bounds=[80, 46],
            padding=5,
            button_controller=controller,
            # canvas = canvas,
            plot_overlay=plot_overlay,
            plotname=name,
        )
        toolbar.add(button)
        canvas.overlays.append(plot_overlay)
    controller.plot = scatterplot
    controller.plot_overlay = overlay
    canvas.overlays.append(overlay)

    return toolbar


class PlotFrame(DemoFrame):
    def _create_viewport(self):
        # Create a container and add our plots
        canvas = PlotCanvas()
        canvas.range_controller = RangeController(cavas=canvas)

        toolbar = make_toolbar(canvas)
        toolbar.component = canvas
        canvas.overlays.append(toolbar)

        viewport = Viewport(component=canvas)
        if MULTITOUCH:
            viewport.tools.append(MPViewportPanTool(viewport))
        else:
            viewport.tools.append(
                ViewportPanTool(viewport, drag_button="right")
            )
        return viewport

    def _create_window_mt(self):
        viewport = self._create_viewport()

        from enactable.configuration import arg_parser, get_global_config
        from enactable.enable.enable_blob_listener import BlobWindow
        from enactable.enable.blobprovider import NetworkBlobProvider

        parser = arg_parser()
        args = parser.parse_args()
        cfg = get_global_config()
        tconf = cfg.tconf
        tconf.from_arguments(args)

        provider = NetworkBlobProvider(
            host=tconf.Server.host, port=tconf.Server.port
        )
        provider.start()
        return BlobWindow(self, -1, component=viewport, blob_provider=provider)

    def _create_window_simple(self):
        viewport = self._create_viewport()
        return Window(self, -1, component=viewport)

    def _create_window(self):
        if MULTITOUCH:
            return self._create_window_mt()
        else:
            return self._create_window_simple()


if __name__ == "__main__":
    # Save demo so that it doesn't get garbage collected when run within
    # existing event loop (i.e. from ipython).
    demo = demo_main(PlotFrame, size=(1000, 700), title="PlotCanvas")
