"""
Visualization of simulated live data stream

Shows how Chaco and Traits can be used to easily build a data
acquisition and visualization system.

Two frames are opened: one has the plot and allows configuration of
various plot properties, and one which simulates controls for the hardware
device from which the data is being acquired; in this case, it is a mockup
random number generator whose mean and standard deviation can be controlled
by the user.
"""

# Major library imports
import numpy as np

# Enthought imports
from enable.api import ComponentEditor
from traits.api import (
    Array,
    Callable,
    Enum,
    Float,
    HasTraits,
    Instance,
    Int,
    observe,
    Trait,
)
from traitsui.api import Group, HGroup, Item, UItem, View, spring, Handler
from pyface.timer.api import Timer

# Chaco imports
from chaco.api import ArrayPlotData, Plot


class Viewer(HasTraits):
    """This class just contains the two data arrays that will be updated
    by the Controller.  The visualization/editor for this class is a
    Chaco plot.
    """

    index = Array()

    data = Array()

    plot_type = Enum("line", "scatter")

    plot = Instance(Plot)

    def _plot_default(self):
        plot = Plot(ArrayPlotData(x=self.index, y=self.data))
        plot.x_axis.title = "Time"
        plot.y_axis.title = "Signal"

        plot.plot(
            ("x", "y"), type=self.plot_type, name=self.plot_type, color="blue"
        )

        return plot

    @observe("index,data")
    def _update_plot_data(self, event):
        if event.name == "index":
            self.plot.data.set_data("x", self.index)
        else:
            self.plot.data.set_data("y", self.data)

    @observe("plot_type")
    def _update_plot_type(self, event):
        old_plot_type, new_plot_type = event.old, event.new

        self.plot.delplot(old_plot_type)
        self.plot.plot(
            ("x", "y"), type=new_plot_type, name=new_plot_type, color="blue"
        )
        self.plot.invalidate_and_redraw()

    traits_view = View(
        UItem("plot", editor=ComponentEditor()),
        HGroup(spring, Item("plot_type", style="custom"), spring),
        resizable=True,
        buttons=["OK"],
        width=800,
        height=500,
    )


class Controller(HasTraits):

    # A reference to the plot viewer object
    viewer = Instance(Viewer)

    # Some parameters controller the random signal that will be generated
    distribution_type = Enum("normal", "lognormal")
    mean = Float(0.0)
    stddev = Float(1.0)

    # The max number of data points to accumulate and show in the plot
    max_num_points = Int(100)

    # The number of data points we have received; we need to keep track of
    # this in order to generate the correct x axis data series.
    num_ticks = Int(0)

    # private reference to the random number generator.  this syntax
    # just means that self._generator should be initialized to
    # random.normal, which is a random number function, and in the future
    # it can be set to any callable object.
    _generator = Trait(np.random.normal, Callable)

    view = View(
        Group(
            "distribution_type",
            "mean",
            "stddev",
            "max_num_points",
            orientation="vertical",
        ),
        buttons=["OK", "Cancel"],
    )

    def timer_tick(self, *args):
        """
        Callback function that should get called based on a timer tick.  This
        will generate a new random data point and set it on the `.data` array
        of our viewer object.
        """
        # Generate a new number and increment the tick count
        new_val = self._generator(self.mean, self.stddev)
        self.num_ticks += 1

        # grab the existing data, truncate it, and append the new point.
        # This isn't the most efficient thing in the world but it works.
        cur_data = self.viewer.data
        new_data = np.hstack((cur_data[-self.max_num_points + 1:], [new_val]))
        new_index = np.arange(
            self.num_ticks - len(new_data) + 1, self.num_ticks + 0.01
        )

        self.viewer.index = new_index
        self.viewer.data = new_data

    def _distribution_type_changed(self):
        # This listens for a change in the type of distribution to use.
        if self.distribution_type == "normal":
            self._generator = np.random.normal
        else:
            self._generator = np.random.lognormal


class DemoHandler(Handler):
    def closed(self, info, is_ok):
        """Handles a dialog-based user interface being closed by the user.
        Overridden here to stop the timer once the window is destroyed.
        """

        info.object.timer.Stop()


class Demo(HasTraits):
    controller = Instance(Controller)
    viewer = Instance(Viewer, ())
    timer = Instance(Timer)
    view = View(
        Item("controller", style="custom", show_label=False),
        Item("viewer", style="custom", show_label=False),
        handler=DemoHandler,
        resizable=True,
    )

    def edit_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(100, self.controller.timer_tick)
        return super(Demo, self).edit_traits(*args, **kws)

    def configure_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(100, self.controller.timer_tick)
        return super(Demo, self).configure_traits(*args, **kws)

    def _controller_default(self):
        return Controller(viewer=self.viewer)


# NOTE: examples/demo/demo.py looks for a 'demo' or 'popup' or 'modal popup'
# keyword when it executes this file, and displays a view for it.
popup = Demo()


if __name__ == "__main__":
    popup.configure_traits()
