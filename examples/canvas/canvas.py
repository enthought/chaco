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
        Plot, jet
#from enthought.chaco2.example_support import COLOR_PALETTE
from enthought.chaco2.tools.api import PanTool, SimpleZoom , LegendTool

# Canvas imports
from enthought.chaco2.plot_canvas import PlotCanvas
from enthought.chaco2.plot_canvas_toolbar import PlotCanvasToolbar, PlotToolbarButton
from transient_plot_overlay import TransientPlotOverlay

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

    # A reference to the Plot object that displays scatterplots of multiple
    # dataseries
    plot = Instance(Plot)

    # The transient plot overlay housing self.plot
    plot_overlay = Any

    def notify(self, button, type, event):
        """ Informs the controller that the particular **button** just
        got an event.  **Type** is either "up" or "down".  Event is the
        actual mouse event.
        """
        if getattr(event, self.modifier + "_down", True):
            if type == "down":
                self.button_selected(button)
            elif type == "up":
                # This is to allow the mouse to simulate multitouch;
                # If ctrl is down when the button is released, pretend
                # it didn't actually come up
                pass
        else:
            #self.active_buttons = [button]
            if type == "down":
                if button not in self.active_buttons:
                    # Deselect all current buttons and select the new one
                    [self.button_deselected(b) for b in self.active_buttons]
                    self.button_selected(button)
            elif type == "up":
                if button in self.active_buttons:
                    self.button_deselected(button)

        ## Reconcile the list of active buttons and their plots
        #active_names = [b.plotname for b in self.active_buttons]
        #for p in self.plot.plots.keys():
        #    if p in active_names:
        #        self.plot.showplot(p)
        #    else:
        #        self.plot.hideplot(p)
        return

    def button_selected(self, button):
        if button not in self.active_buttons:
            self.active_buttons.append(button)
        numbuttons = len(self.active_buttons)
        if numbuttons == 1:
            self.active_buttons[0].show_overlay()
        elif numbuttons in (2,3):
            self.active_buttons[0].hide_overlay()
            self.show_scatterplot(*self.active_buttons)
        else:
            # Show the first two vs. the last one
            self.show_scatterplot(self.active_buttons[0], self.active_buttons[1],
                                  self.active_buttons[-1])
        return


    def button_deselected(self, button):
        if button in self.active_buttons:
            self.active_buttons.remove(button)
        numbuttons = len(self.active_buttons)
        if numbuttons == 0:
            button.hide_overlay()
        elif numbuttons == 1:
            self.hide_scatterplot()
            self.active_buttons[0].show_overlay()
        elif numbuttons in (2,3):
            self.show_scatterplot(*self.active_buttons)
        else:
            self.show_scatterplot(self.active_buttons[0], self.active_buttons[1],
                                  self.active_buttons[-1])
        return

    def show_scatterplot(self, b1, b2, b3=None):
        if len(self.plot.plots) > 0:
            self.plot.delplot(self.plot.plots.keys()[0])

        if b3 is None:
            cur_plot = self.plot.plot((b1.plotname+"_y", b2.plotname+"_y"), type="scatter",
                                      marker="circle",
                                      color="red",
                                      marker_size=4,
                                      )

        else:
            cur_plot = self.plot.plot((b1.plotname+"_y", b2.plotname+"_y", b3.plotname+"_y"),
                                      type="cmap_scatter",
                                      marker="circle",
                                      marker_size=4,
                                      color_mapper=jet,
                                      )
        self.plot_overlay.visible = True
        self.plot.request_redraw()

    def hide_scatterplot(self):
        self.plot_overlay.visible = False
        


class DataSourceButton(PlotToolbarButton):
    
    # The timeseries plot of this datasource
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
        self.request_redraw()
        return

    def hide_overlay(self):
        if self._overlay is not None:
            self._overlay.visible = False
        self.request_redraw()
        return

    def _do_layout(self):
        self._overlay.do_layout()

    def _plot_changed(self, old, new):
        if new is not None:
            if self._overlay is None:
                self._overlay = TransientPlotOverlay(component = self,
                                                     border_visible=True)
            
            self._overlay.overlay_component = new
        return


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
    add_basic_tools(plot)
    plot.x_axis.visible = False
    plot.plot((xname, yname), name=name, type="line", color="blue",)
    return plot
    
def make_toolbar():
    toolbar = PlotCanvasToolbar(bounds=[70, 200], 
                                position=[50,350],
                                fill_padding=True,
                                bgcolor="lightgrey",
                                padding = 5,
                                align = "left",
                                )
    controller = ButtonController()
    
    buttons = []
    pd = ArrayPlotData()
    for name in DATA.keys():
        plot = do_plot(name, pd)
        toolbar.add(DataSourceButton(label=name, 
                                bounds=[60,24],
                                padding = 5,
                                button_controller = controller,
                                plot = plot,
                                plotname = name))

    scatterplot = Plot(pd, padding=15, bgcolor="white", unified_draw=True,
                       border_visible=True)
    add_basic_tools(scatterplot)
    controller.plot = scatterplot
    controller.plot_overlay = TransientPlotOverlay(component=toolbar,
                                 overlay_component=scatterplot,
                                 bounds=[500,500],
                                 border_visible=True,
                                 visible = False,  # initially invisible
                                 )
    toolbar.overlays.append(controller.plot_overlay)
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
        toolbar = make_toolbar()
        canvas.add(*plots)
        #canvas.add(make_toolbar())
        toolbar.component = canvas
        canvas.overlays.append(toolbar)

        viewport = Viewport(component=canvas)
        viewport.tools.append(ViewportPanTool(viewport, drag_button="right"))

        # Return a window containing our plots
        return Window(self, -1, component=viewport)
        
if __name__ == "__main__":
    demo_main(PlotFrame, size=(1000,700), title="PlotCanvas")

# EOF
