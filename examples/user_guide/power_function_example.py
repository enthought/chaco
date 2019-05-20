# (C) Copyright 2010-2019 Enthought, Inc., Austin, TX
# All rights reserved.

import numpy as np

from chaco.api import ArrayPlotData, Plot
from enable.api import ComponentEditor
from traits.api import Array, HasStrictTraits, Instance, Range, on_trait_change
from traitsui.api import Item, VGroup, View


class PowerFunctionExample(HasStrictTraits):
    """ Display a plot of a power function. """

    #: The plot holding the visualization
    plot = Instance(Plot)

    #: The power of the monomial to use.
    power = Range(0, 5, value=2)

    #: The x-values to plot.
    x = Array(shape=(None,), dtype='float')

    # Trait defaults --------------------------------------------------------

    def _plot_default(self):
        y = self.x**self.power
        plot_data = ArrayPlotData(x=self.x, y=y)
        plot = Plot(plot_data)
        plot.plot(
            ('x', 'y'),
            'line',
            name="power function",
            color='auto'
        )

        # configure the plot
        plot.padding_top = 25
        plot.border_visible = False
        plot.index_grid.visible = False
        plot.value_grid.visible = False
        plot.title = "Power Function n={}".format(self.power)
        plot.title_position = 'right'
        plot.title_angle = -90
        plot.legend_alignment = 'ul'
        plot.legend.border_visible = False
        plot.legend.bgcolor = (0.9, 0.9, 0.9, 0.5)
        plot.legend.visible = True

        plot.index_axis.title = "y"
        plot.value_axis.title = "x"

        return plot

    def _x_default(self):
        return np.linspace(-2.0, 2.0, 101)

    # Trait change handlers -------------------------------------------------

    @on_trait_change('power')
    def _update_y(self):
        y = self.x**self.power
        self.plot.data.set_data('y', y)

    @on_trait_change('x')
    def _update_data(self):
        y = self.x**self.power
        self.plot.data.update_data(x=self.x, y=y)

    @on_trait_change('power')
    def _update_title(self):
        self.plot.title = "Power Function n={}".format(self.power)

    # TraitsUI view ---------------------------------------------------------

    view = View(
        VGroup(
            Item('plot', editor=ComponentEditor()),
            VGroup(
                Item('power'),
            ),
            show_labels=False,
        ),
        resizable=True,
        title="Power Function Example"
    )


if __name__ == '__main__':
    view = PowerFunctionExample()
    view.configure_traits()
