#!/usr/bin/env python
"""
The main app for the PlotCanvas application
"""

# Major library imports
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
        Plot, PlotComponent 
from enthought.chaco2.example_support import COLOR_PALETTE
from enthought.chaco2.tools.api import PanTool, SimpleZoom , LegendTool

# Canvas imports
from enthought.chaco2.plot_canvas import PlotCanvas
from enthought.chaco2.plot_canvas_toolbar import PlotCanvasToolbar, PlotToolbarButton

DATA = {
    "GOOG": random.uniform(-2.0, 10.0, 100),
    "MSFT": random.uniform(-2.0, 10.0, 100),
    "AAPL": random.uniform(-2.0, 10.0, 100),
    "YHOO": random.uniform(-2.0, 10.0, 100),
    "CSCO": random.uniform(-2.0, 10.0, 100),
    "INTC": random.uniform(-2.0, 10.0, 100),
    "ORCL": random.uniform(-2.0, 10.0, 100),
    "HPQ": random.uniform(-2.0, 10.0, 100),
    "DELL": random.uniform(-2.0, 10.0, 100),
    }


class ButtonController(HasTraits):
    """ Tells buttons what to do 
    
    Buttons defer to this when they are activated.
    """
    
    modifier = Enum("control", "shift", "alt")
    
    # The list of buttons that are currently "down"
    active_buttons = List
    
    # A reference to the plot to add 
    plot = Instance(Plot)
    
    def notify(self, button, type, event):
        """ Informs the controller that the particular **button** just
        got an event.  **Type** is either "up" or "down".  Event is the
        actual mouse event.
        """
        if getattr(event, self.modifier + "_down", True):
            if type == "down":
                print "mouse down, control down"
                if button in self.active_buttons:
                    self.active_buttons.remove(button)
                else:
                    self.active_buttons.append(button)
                print "New buttons:", self.active_buttons
        else:
            self.active_buttons = [button]

        # Reconcile the list of active buttons and their plots
        active_names = [b.plotname for b in self.active_buttons]
        for p in self.plot.plots.keys():
            if p in active_names:
                self.plot.showplot(p)
            else:
                self.plot.hideplot(p)

        if type == "up":
            button.hide_overlay()
        elif type == "down":
            button.show_overlay()
        return


class DataSourceButton(PlotToolbarButton):
    
    # The plot to show when this button is active
    plot = Any()
    
    plotname = Str
    
    #overlay_bounds = List()
    
    # Can't call this "controller" because it conflicts with old tool dispatch
    button_controller = Instance(ButtonController)
    
    # Override inherited trait
    label_color = (0,0,0,1)

    resizable = ""
    
    # The overlay to display when the user holds the mouse down over us.
    _overlay = Instance(AbstractOverlay)
    
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
        if self._overlay is not None:
            if self._overlay not in self.overlays:
                self.overlays.append(self._overlay)
            self._overlay.visible = True
        return

    def hide_overlay(self):
        if self._overlay is not None:
            self._overlay.visible = False
        return

    def _do_layout(self):
        self._overlay.do_layout()

    def _plot_changed(self, old, new):
        if new is not None:
            if self._overlay is None:
                self._overlay = TransientPlotOverlay(component = self,
                                                     bgcolor = "red",
                                                     border_visible=True)
            
            self._overlay.overlay_component = new
        return


class TransientPlotOverlay(AbstractOverlay):
    """ Allows an arbitrary plot component to be overlaid on top of another one.
    """
    
    # The PlotComponent to draw as an overlay
    overlay_component = Instance(PlotComponent)

    # Where this overlay should draw relative to our .component
    align = Enum("right", "left", "top", "bottom")

    # The amount of space between the overlaying component and the underlying
    # one.  This is either horizontal or vertical (depending on the value of
    # self.align), but is not both.
    margin = Float(10)

    # Override default values of some inherited traits
    unified_draw = True

    def _bounds_default(self):
        return [350, 150]

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        self._do_layout()
        gc.save_state()
        gc.clear_clip_path()
        self.overlay_component._draw(gc, view_bounds, mode)
        gc.restore_state()

    def _do_layout(self):
        component = self.component
        bounds = self.outer_bounds

        if self.align in ("right", "left"):
            y = component.outer_y -(bounds[1] - component.outer_height) / 2
            if self.align == "right":
                x = component.outer_x2 + self.margin
            else:
                x = component.outer_x - bounds[0] - self.margin

        else:   # "top", "bottom"
            x = component.outer_x -(bounds[0] - component.outer_width) / 2
            if self.align == "top":
                y = component.outer_y2 + self.margin
            else:
                y = component.outer_y - bounds[1] - self.margin
        
        overlay_component = self.overlay_component
        overlay_component.outer_bounds = self.outer_bounds
        overlay_component.outer_position = [x, y]
        overlay_component._layout_needed = True
        overlay_component.do_layout()


def add_basic_tools(plot):
        plot.tools.append(PanTool(plot))
        plot.tools.append(MoveTool(plot, drag_button="right"))
        zoom = SimpleZoom(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

def do_plot(name, pd=None, plot=None):
    if pd is None:
        pd = ArrayPlotData()
    xname = name + "_x"
    yname = name + "_y"
    pd.set_data(xname, range(len(DATA[name])))
    pd.set_data(yname, DATA[name])
    
    if plot is None:
        plot = Plot(pd, 
                    padding = 15,
                    border_visible = True,)
        plot.x_axis.visible = False
    plot.plot((xname, yname), name=name, type="line", color="blue",)
    return plot
    
def make_toolbar():
    toolbar = PlotCanvasToolbar(bounds=[60, 200], 
                                position=[50,350],
                                bgcolor="lightgrey")
    toolbar.padding = 5
    
    controller = ButtonController()
    
    plot = None
    buttons = []
    for name in DATA.keys():
        if plot is None:
            plot = do_plot(name)
        else:
            do_plot(name, plot.data, plot)
        buttons.append(DataSourceButton(label=name, 
                                bounds=[60,24],
                                padding = 5,
                                button_controller = controller,
                                plot = plot,
                                plotname = name))
    controller.plot = plot
    toolbar.add(*buttons)
    toolbar.tools.append(MoveTool(toolbar, drag_button="right"))
    return toolbar

def make_default_plots():
    # Create some x-y data series to plot
    x = linspace(-2.0, 10.0, 100)
    pd = ArrayPlotData(index = x)
    for i in range(5):
        pd.set_data("y" + str(i), jn(i,x))

    # Create some line plots of some of the data
    plot1 = Plot(pd, resizable="", bounds=[300,300],
                 position=[100, 100],
                 border_visible=True,
                 unified_draw = True)
    plot1.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="red")
    plot1.plot(("index", "y3"), name="j_3", color="blue")

    # Tweak some of the plot properties
    #plot1.title = "Line Plot"
    plot1.padding = 50
    #plot1.legend.visible = True
    #plot1.legend.tools.append(LegendTool(plot1.legend, drag_button="right"))

    # Create a second scatter plot of one of the datasets, linking its 
    # range to the first plot
    plot2 = Plot(pd, range2d=plot1.range2d, padding=50,
                 resizable="", bounds=[300,300], position=[500,100],
                 border_visible=True,
                 unified_draw = True,
                 bgcolor = (1,1,1,0.8))
    plot2.plot(('index', 'y3'), type="scatter", color="blue", 
               marker_size=10, marker="circle")
    
    add_basic_tools(plot1)
    add_basic_tools(plot2)
    return plot1, plot2


class PlotFrame(DemoFrame):

    def _create_window(self):
        # Create a container and add our plots
        canvas = PlotCanvas()

        plots = make_default_plots()
        canvas.add(*plots)
        canvas.add(make_toolbar())

        viewport = Viewport(component=canvas)
        viewport.tools.append(ViewportPanTool(viewport, drag_button="right"))

        # Return a window containing our plots
        return Window(self, -1, component=viewport)
        
if __name__ == "__main__":
    demo_main(PlotFrame, size=(1000,700), title="PlotCanvas")

# EOF
