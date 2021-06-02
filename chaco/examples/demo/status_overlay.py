"""
Displays a plot with a few buttons to control which overlay to display
"""
import numpy

from chaco.api import Plot, ArrayPlotData
from chaco.overlays.api import ErrorLayer, WarningLayer, StatusLayer
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance, Button
from traitsui.api import UItem, View, HGroup


class MyPlot(HasTraits):
    """Displays a plot with a few buttons to control which overlay
    to display
    """

    plot = Instance(Plot)
    status_overlay = Instance(StatusLayer)

    error_button = Button("Error")
    warn_button = Button("Warning")
    no_problem_button = Button("No problem")

    def _plot_default(self):
        index = numpy.array([1, 2, 3, 4, 5])
        data_series = index ** 2

        plot_data = ArrayPlotData(index=index)
        plot_data.set_data("data_series", data_series)
        plot = Plot(plot_data)
        plot.plot(("index", "data_series"))

        return plot

    def _error_button_fired(self, event):
        """removes the old overlay and replaces it with
        an error overlay
        """
        self.clear_status()

        self.status_overlay = ErrorLayer(
            component=self.plot, align="ul", scale_factor=0.25
        )
        self.plot.overlays.append(self.status_overlay)

        self.plot.request_redraw()

    def _warn_button_fired(self, event):
        """removes the old overlay and replaces it with
        an warning overlay
        """
        self.clear_status()

        self.status_overlay = WarningLayer(
            component=self.plot, align="ur", scale_factor=0.25
        )
        self.plot.overlays.append(self.status_overlay)

        self.plot.request_redraw()

    def _no_problem_button_fired(self, event):
        """removes the old overlay"""
        self.clear_status()
        self.plot.request_redraw()

    def clear_status(self):
        if self.status_overlay in self.plot.overlays:
            # fade_out will remove the overlay when its done
            self.status_overlay.fade_out()

    traits_view = View(
        HGroup(
            UItem("error_button"),
            UItem("warn_button"),
            UItem("no_problem_button"),
        ),
        UItem("plot", editor=ComponentEditor()),
        width=700,
        height=600,
        resizable=True,
    )


my_plot = MyPlot()
my_plot.configure_traits()
