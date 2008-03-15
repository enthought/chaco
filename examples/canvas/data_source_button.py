
from random import choice
from enthought.traits.api import Any, Enum, HasTraits, Instance, Int, List, Str
from enthought.chaco2.example_support import COLOR_PALETTE
from enthought.chaco2.api import Plot
from enthought.chaco2.plot_canvas_toolbar import PlotToolbarButton

DEBUG = False

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

    cur_bid = Int(-1)
    
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

    def normal_blob_down(self, event):
        if self.cur_bid == -1:
            self.cur_bid = event.bid
            self.normal_left_down(event)
    
    def normal_blob_up(self, event):
        if event.bid == self.cur_bid:
            self.cur_bid = -1
            self.normal_left_up(event)
    
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
