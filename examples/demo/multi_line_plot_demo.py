"""
Demonstrates the MultiLinePlot.

This demo assumes that 'model', an instance of DataModel containing the 2D
data to be plotted, will be given to the constructor, and will not change
later.
"""
import numpy as np

from traits.api import Instance, HasTraits, Range, Array
from traitsui.api import View, Item, HGroup, VGroup, Group

from enable.api import ComponentEditor

from chaco.api import (
    LinearMapper,
    Plot,
    ArrayDataSource,
    DataRange1D,
    PlotAxis,
    MultiArrayDataSource,
    MultiLinePlot
)


class DataModel(HasTraits):
    """This is the data to be plotted in the demo."""

    # The x values of the data (1D numpy array).
    x_index = Array()

    # The channel numbers (1D numpy array).
    y_index = Array()

    # The data.  The shape of this 2D array must be (y_index.size, x_index.size)
    data = Array()


class MultiLinePlotDemo(HasTraits):

    model = Instance(DataModel)

    plot = Instance(Plot)

    multi_line_plot_renderer = Instance(MultiLinePlot)

    # Drives multi_line_plot_renderer.normalized_amplitude
    amplitude = Range(-1.5, 1.5, value=-0.5)

    # Drives multi_line_plot_renderer.offset
    offset = Range(-1.0, 1.0, value=0)

    traits_view = View(
        VGroup(
            Group(
                Item("plot", editor=ComponentEditor(), show_label=False),
            ),
            HGroup(
                Item("amplitude", springy=True),
                Item("offset", springy=True),
                springy=True,
            ),
            HGroup(
                Item("object.multi_line_plot_renderer.color", springy=True),
                Item(
                    "object.multi_line_plot_renderer.line_style", springy=True
                ),
                springy=True,
            ),
        ),
        width=800,
        height=500,
        resizable=True,
    )

    # -----------------------------------------------------------------------
    # Trait defaults
    # -----------------------------------------------------------------------

    def _multi_line_plot_renderer_default(self):
        """Create the default MultiLinePlot instance."""

        xs = ArrayDataSource(self.model.x_index, sort_order="ascending")
        xrange = DataRange1D()
        xrange.add(xs)

        ys = ArrayDataSource(self.model.y_index, sort_order="ascending")
        yrange = DataRange1D()
        yrange.add(ys)

        # The data source for the MultiLinePlot.
        ds = MultiArrayDataSource(data=self.model.data)

        multi_line_plot_renderer = MultiLinePlot(
            index=xs,
            yindex=ys,
            index_mapper=LinearMapper(range=xrange),
            value_mapper=LinearMapper(range=yrange),
            value=ds,
            global_max=self.model.data.max(),
            global_min=self.model.data.min(),
        )

        return multi_line_plot_renderer

    def _plot_default(self):
        """Create the Plot instance."""

        plot = Plot(title="MultiLinePlot Demo")
        plot.add(self.multi_line_plot_renderer)

        x_axis = PlotAxis(
            component=plot,
            mapper=self.multi_line_plot_renderer.index_mapper,
            orientation="bottom",
            title="t (seconds)",
        )
        y_axis = PlotAxis(
            component=plot,
            mapper=self.multi_line_plot_renderer.value_mapper,
            orientation="left",
            title="channel",
        )
        plot.overlays.extend([x_axis, y_axis])
        return plot

    # -----------------------------------------------------------------------
    # Trait change handlers
    # -----------------------------------------------------------------------

    def _amplitude_changed(self, amp):
        self.multi_line_plot_renderer.normalized_amplitude = amp

    def _offset_changed(self, off):
        self.multi_line_plot_renderer.offset = off
        # FIXME:  The change does not trigger a redraw.  Force a redraw by
        # faking an amplitude change.
        self.multi_line_plot_renderer._amplitude_changed()


if __name__ == "__main__":
    # Sample rate.
    fs = 500
    # Total time.
    T = 5.0
    num_samples = fs * T
    t = np.arange(num_samples) / fs

    channels = np.arange(12)
    # Frequencies of the sine functions in each channel.
    freqs = 3 * (channels[:, None] + 1)
    y = np.sin(freqs * t)

    # Create an instance of DataModel.  This is the data to
    # be plotted with a MultiLinePlot.
    data = DataModel(x_index=t, y_index=channels, data=y)

    # Create the demo class, and show it.
    demo = MultiLinePlotDemo(model=data)
    demo.configure_traits()
