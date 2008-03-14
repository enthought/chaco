#!/usr/bin/env python
"""
The main app for the PlotCanvas application
"""

# Major library imports
from copy import copy
from random import choice
from numpy import arange, fabs, linspace, pi, sin
from numpy import random
from scipy.special import jn


# Enthought library imports
from enthought.enable2.api import Viewport, Window
from enthought.enable2.tools.api import MoveTool, ViewportPanTool
from enthought.enable2.example_support import DemoFrame, demo_main
from enthought.traits.api import Any, Bool, Enum, Float, HasTraits, Instance, \
                                 List, Str


# Chaco imports
from enthought.chaco2.api import AbstractOverlay, ArrayPlotData, \
        Plot, jet, ScatterPlot, LinePlot, LinearMapper
from enthought.chaco2.example_support import COLOR_PALETTE
from enthought.chaco2.tools.api import PanTool, SimpleZoom , LegendTool

# Canvas imports
from enthought.chaco2.plot_canvas import PlotCanvas
from enthought.chaco2.plot_canvas_toolbar import PlotCanvasToolbar, PlotToolbarButton
from transient_plot_overlay import TransientPlotOverlay
from plot_clone_tool import PlotCloneTool
#from canvas_grid import CanvasGrid



DEBUG = False

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

class ButtonController(HasTraits):
    """ Tells buttons what to do 
    
    Buttons defer to this when they are activated.
    """
    
    modifier = Enum("control", "shift", "alt")
    
    # The list of buttons that are currently "down"
    active_buttons = List

    # A reference to the Plot object that displays scatterplots of multiple
    # dataseries
    plot = Instance(Plot)

    # The transient plot overlay housing self.plot
    plot_overlay = Any

    # The name of the scatter plot in the Plot
    _scatterplot_name = "ButtonControllerPlot"

    def notify(self, button, type, event):
        """ Informs the controller that the particular **button** just
        got an event.  **Type** is either "up" or "down".  Event is the
        actual mouse event.
        """
        control_down = getattr(event, self.modifier + "_down", False)
        if DEBUG:
            print "[notify]", button.plotname, type, "control:", control_down
        if type == "down":
            if control_down and button in self.active_buttons:
                self.button_deselected(button)
            else:
                if not control_down:
                    # Deselect all current buttons and select the new one
                    [self.button_deselected(b) for b in self.active_buttons \
                            if b is not button]
                self.button_selected(button)
        else:  # type == "up"
            if not control_down:
                self.button_deselected(button)
        return

    def button_selected(self, button):
        if DEBUG:
            print "active:", [b.plotname for b in self.active_buttons]
            print "new button selected:", button.plotname
        if button in self.active_buttons:
            return
        numbuttons = len(self.active_buttons)
        if numbuttons == 0:
            self.active_buttons.append(button)
            button.show_overlay()
        elif numbuttons == 1:
            self.active_buttons[0].hide_overlay()
            self.active_buttons.append(button)
            self.show_scatterplot(*self.active_buttons)
        elif numbuttons == 2:
            # Replace the last active button with the new one
            self.active_buttons[1].button_state = "up"
            self.active_buttons[1] = button
            self.hide_scatterplot()
            self.show_scatterplot(*self.active_buttons)
        else:
            return
        button.button_state = "down"
        return

    def button_deselected(self, button):
        if DEBUG:
            print "active:", [b.plotname for b in self.active_buttons]
            print "new button deselected:", button.plotname
        if button not in self.active_buttons:
            button.button_state = "up"
            return
        numbuttons = len(self.active_buttons)
        if numbuttons == 1:
            if button in self.active_buttons:
                self.active_buttons.remove(button)
            button.hide_overlay()
        elif numbuttons == 2:
            if button in self.active_buttons:
                self.active_buttons.remove(button)
                self.hide_scatterplot()
                remaining_button = self.active_buttons[0]
                remaining_button.show_overlay()
        else:
            return
        button.button_state = "up"
        return

    def show_scatterplot(self, b1, b2):
        if len(self.plot.plots) > 0:
            self.plot.delplot(*self.plot.plots.keys())

        cur_plot = self.plot.plot((b1.plotname+"_y", b2.plotname+"_y"), 
                                  name=self._scatterplot_name,
                                  type="scatter",
                                  marker="square",
                                  color=tuple(choice(COLOR_PALETTE)),
                                  marker_size=8,
                                  )
        self.plot.index_axis.title = b1.plotname
        #self.plot.value_axis.title = b2.plotname
        self.plot.title = b1.plotname + " vs. " + b2.plotname
        self.plot_overlay.visible = True
        self.plot.request_redraw()

    def hide_scatterplot(self):
        if self._scatterplot_name in self.plot.plots:
            self.plot.delplot(self._scatterplot_name)
            self.plot.index_range.set_bounds("auto", "auto")
            self.plot.value_range.set_bounds("auto", "auto")
        self.plot_overlay.visible = False
        


class DataSourceButton(PlotToolbarButton):
    
    # A TransientPlotOverlay containing the timeseries plot of this datasource
    plot_overlay = Any
    
    plotname = Str

    canvas = Any
    
    #overlay_bounds = List()
    
    # Can't call this "controller" because it conflicts with old tool dispatch
    button_controller = Instance(ButtonController)
    
    # Override inherited trait
    label_color = (0,0,0,1)

    resizable = ""
    
    # The overlay to display when the user holds the mouse down over us.
    #_overlay = Instance(AbstractOverlay)

    def normal_left_down(self, event):
        self.button_state = "down"
        self.button_controller.notify(self, "down", event)
        event.handled = True
        self.request_redraw()
    
    def normal_left_up(self, event):
        self.button_state = "up"
        self.button_controller.notify(self, "up", event)
        event.handled = True
        self.request_redraw()
    
    def normal_mouse_leave(self, event):
        if event.left_down:
            return self.normal_left_up(event)
    
    def normal_mouse_enter(self, event):
        if event.left_down:
            return self.normal_left_down(event)

    def show_overlay(self):
        if self.plot_overlay is not None:
            self._do_layout()
            self.plot_overlay.visible = True
        self.request_redraw()
        return

    def hide_overlay(self):
        if self.plot_overlay is not None:
            self.plot_overlay.visible = False
        self.request_redraw()
        return

    def _do_layout(self):
        if self.canvas is not None:
            boff = self.canvas.bounds_offset
            self.plot_overlay.offset = (boff[0],
                    boff[1] + self.y - self.container.y + self.height/2)
        self.plot_overlay.do_layout()


def add_basic_tools(plot):
    plot.tools.append(PanTool(plot))
    plot.tools.append(MoveTool(plot, drag_button="right"))
    zoom = SimpleZoom(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

def do_plot(name, pd):
    xname = name + "_x"
    yname = name + "_y"
    pd.set_data(xname, range(len(DATA[name])))
    pd.set_data(yname, DATA[name])
    
    plot = Plot(pd, padding = 15,
                unified_draw = True,
                border_visible = True,
                )
    plot.x_axis.visible = False
    plot.title = name
    plot.plot((xname, yname), name=name, type="line", color="blue",)
    return plot

def clone_renderer(r):
    """ Returns a clone of plot renderer r """
    basic_traits = ["orientation", "line_width", "color", "outline_color", 
                    "bgcolor", "border_visible", "border_color", "visible",
                    "fill_padding", "resizable", "aspect_ratio",
                    "draw_layer", "draw_order", "border_width", "resizable",
                    "index", "value",]

    scatter_traits = ["custom_symbol", "marker", "marker_size", "selection_marker",
                      "selection_marker_size", "selection_line_width",
                      "selection_color"]

    line_traits = ["selected_color", "selected_line_style", "metadata_name",
                   "render_style"]

    if isinstance(r, ScatterPlot):
        return r.clone_traits(basic_traits + scatter_traits)
    elif isinstance(r, LinePlot):
        return r.clone_traits(basic_traits + line_traits)

def clone_plot(clonetool, drop_position):
    # Create a new Plot object
    oldplot = clonetool.component
    newplot = Plot(oldplot.data)
    basic_traits = ["orientation", "default_origin", "bgcolor", "border_color",
                    "border_width", "border_visible", "draw_layer", "unified_draw",
                    "fit_components", "fill_padding", "visible", "aspect_ratio",
                    "title"]
                   
    for attr in basic_traits:
        setattr(newplot, attr, getattr(oldplot, attr))

    # copy the ranges
    dst = newplot.range2d
    src = oldplot.range2d
    #for attr in ('_low_setting', '_low_value', '_high_setting', '_high_value'):
    #    setattr(dst, attr, getattr(src, attr))
    dst._xrange.sources = copy(src._xrange.sources)
    dst._yrange.sources = copy(src._yrange.sources)

    newplot.padding = oldplot.padding
    newplot.bounds = oldplot.bounds[:]
    newplot.resizable = ""
    newplot.position = drop_position

    newplot.datasources = copy(oldplot.datasources)

    for name, renderers in oldplot.plots.items():
        newrenderers = []
        for renderer in renderers:
            new_r = clone_renderer(renderer)
            new_r.index_mapper = LinearMapper(range=newplot.index_range)
            new_r.value_mapper = LinearMapper(range=newplot.value_range)
            new_r._layout_needed = True
            new_r.invalidate_draw()
            new_r.resizable = "hv"
            #new_r._debug = True
            newrenderers.append(new_r)
        newplot.plots[name] = newrenderers
    #newplot.plots = copy(oldplot.plots)

    for name, renderers in newplot.plots.items():
        newplot.add(*renderers)

    newplot.index_axis.title = oldplot.index_axis.title
    newplot.value_axis.title = oldplot.value_axis.title

    # Add tools to the new plot
    pan_traits = ["drag_button", "constrain", "constrain_key", "constrain_direction",
                  "speed"]
    zoom_traits = ["tool_mode", "always_on", "axis", "enable_wheel", "drag_button",
                   "wheel_zoom_step", "enter_zoom_key", "exit_zoom_key", "pointer",
                   "color", "alpha", "border_color", "border_size", "disable_on_complete",
                   "minimum_screen_delta", "max_zoom_in_factor", "max_zoom_out_factor"]
    move_traits = ["drag_button", "end_drag_on_leave", "cancel_keys", "capture_mouse",
                   "modifier_key"]
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
        if isinstance(tool, SimpleZoom):
            newtool = tool.clone_traits(zoom_traits)
            newtool.component = newplot
            break
    else:
        newtool = SimpleZoom(newplot)
    newplot.tools.append(newtool)

    newplot._layout_needed = True
    newplot.invalidate_draw()

    clonetool.dest.add(newplot)
    return

    
def make_toolbar(canvas):
    # Create the toolbar
    toolbar = PlotCanvasToolbar(bounds=[70, 200], 
                                position=[50,350],
                                fill_padding=True,
                                bgcolor="lightgrey",
                                padding = 5,
                                align = "left",
                                )

    # Create the scatterplot
    pd = ArrayPlotData()
    scatterplot = Plot(pd, padding=15, bgcolor="white", unified_draw=True,
                       border_visible=True)
    scatterplot.tools.append(PanTool(scatterplot, drag_button="right"))
    scatterplot.overlays.append(PlotCloneTool(scatterplot, dest=canvas,
                                              plot_cloner=clone_plot))
    scatterplot.tools.append(SimpleZoom(scatterplot))

    # Create the overlay
    overlay = TransientPlotOverlay(component=toolbar,
                                   overlay_component=scatterplot,
                                   bounds=[350,350],
                                   border_visible=True,
                                   visible = False,  # initially invisible
                                   )
    scatterplot.container = overlay
    
    # Create buttons 
    controller = ButtonController()
    for name in DATA.keys():
        plot = do_plot(name, pd)
        plot.tools.append(PanTool(plot, drag_button="right", constrain=True,
                                  constrain_direction="x"))
        plot.tools.append(SimpleZoom(plot, tool_mode="range", axis="index",
                                     always_on=False))
        plot.overlays.append(PlotCloneTool(plot, dest=canvas,
                                           plot_cloner=clone_plot))
        plot_overlay = TransientPlotOverlay(component=toolbar,
                                            overlay_component=plot,
                                            border_visible=True,
                                            visible=False,
                                            )
        plot.container = plot_overlay
        button = DataSourceButton(label=name, 
                                  bounds=[60,24],
                                  padding = 5,
                                  button_controller = controller,
                                  #canvas = canvas,
                                  plot_overlay = plot_overlay,
                                  plotname = name)
        toolbar.add(button)
        canvas.overlays.append(plot_overlay)
    controller.plot = scatterplot
    controller.plot_overlay = overlay
    canvas.overlays.append(overlay)

    return toolbar


class PlotFrame(DemoFrame):

    def _create_window(self):
        # Create a container and add our plots
        canvas = PlotCanvas()

        toolbar = make_toolbar(canvas)
        toolbar.component = canvas
        canvas.overlays.append(toolbar)

        #grid = CanvasGrid(component=canvas)
        #canvas.underlays.append(grid)

        viewport = Viewport(component=canvas)
        viewport.tools.append(ViewportPanTool(viewport, drag_button="right"))

        # Return a window containing our plots
        return Window(self, -1, component=viewport)
        
if __name__ == "__main__":
    demo_main(PlotFrame, size=(1000,700), title="PlotCanvas")

# EOF
