import numpy as np
 
from enthought.traits.api import Instance, HasTraits, Range
from enthought.traits.ui.api import View, Item, HGroup, VGroup, Group

from enthought.enable.api import ComponentEditor

from enthought.chaco.api import LinearMapper, Plot, ArrayDataSource, DataRange1D, PlotAxis
from enthought.chaco.multi_array_data_source import MultiArrayDataSource
from enthought.chaco.multi_line_plot import MultiLinePlot


class MultiLinePlotDemo(HasTraits):
    """Demonstrates the MultiLinePlot."""

    plot = Instance(Plot)

    multi_line_plot_renderer = Instance(MultiLinePlot)

    amplitude = Range(-1.5, 1.5, value=-0.5)

    offset = Range(-1.0, 1.0, value=0)

    traits_view = \
        View(
            VGroup(
                Group(
                    Item('plot', editor=ComponentEditor(), show_label=False),
                ),
                HGroup(
                    Item('amplitude', springy=True),
                    Item('offset', springy=True),
                    springy=True,
                ),
                HGroup(
                    Item('object.multi_line_plot_renderer.color', springy=True),
                    Item('object.multi_line_plot_renderer.line_style', springy=True),
                    springy=True,
                ),
            ),
            width=800,
            height=500,
            resizable=True,
        )

    def __init__(self, x_index, y_index, data, **kw):
        super(MultiLinePlotDemo, self).__init__(**kw)
        
        # Create the data source for the MultiLinePlot.
        ds = MultiArrayDataSource(data=data)
        
        xs = ArrayDataSource(x_index, sort_order='ascending')
        xrange = DataRange1D()
        xrange.add(xs)
        
        ys = ArrayDataSource(y_index, sort_order='ascending')
        yrange = DataRange1D()
        yrange.add(ys)
        
        self.multi_line_plot_renderer = \
            MultiLinePlot(
                index = xs,
                yindex = ys,
                index_mapper = LinearMapper(range=xrange),
                value_mapper = LinearMapper(range=yrange),
                value=ds,
                global_max = data.max(),
                global_min = data.min(),
                **kw)

        self.plot = Plot(title="MultiLinePlot Demo")
        self.plot.add(self.multi_line_plot_renderer)

        x_axis = PlotAxis(component=self.plot, 
                            mapper=self.multi_line_plot_renderer.index_mapper,
                            orientation='bottom',
                            title='t (seconds)')
        y_axis = PlotAxis(component=self.plot,
                            mapper=self.multi_line_plot_renderer.value_mapper,
                            orientation='left',
                            title='channel')
        self.plot.overlays.extend([x_axis, y_axis])

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
    freqs = 3*(channels[:,None] + 1)
    y = np.sin(freqs * t)

    demo = MultiLinePlotDemo(t, channels, y)
    demo.configure_traits()
