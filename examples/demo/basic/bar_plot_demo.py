"""Demonstrate a simple polygon plot.  The UI allows you to change
some of the attributes of the plot.
"""

import numpy as np

from traits.api import HasTraits, Instance, Range
from traitsui.api import View, UItem, Item, Group, VGroup
from chaco.api import ArrayDataSource, DataRange1D, LinearMapper, BarPlot
from enable.api import ComponentEditor


class BarPlotDemo(HasTraits):

    # The bar plot renderer.
    bar_plot = Instance(BarPlot)

    # Assorted styles that will be set on `bar_plot`.    
    bar_width = Range(0.0, 1.0, 0.8)
    line_width = Range(0.0, 10.0, 5.0)
    alpha = Range(0.0, 1.0, 1.0)
    line_color_alpha = Range(0.0, 1.0, 1.0)
    fill_color_alpha = Range(0.0, 1.0, 1.0)

    traits_view = \
        View(
            VGroup(
                Group(
                    UItem('bar_plot', 
                          editor=ComponentEditor(), 
                          style='custom'),
                ),
                VGroup(
                    Item('bar_width'),
                    Item('line_width'),
                    Item('line_color_alpha'),
                    Item('fill_color_alpha'),
                    Item('alpha'),
                ),
            ),
            resizable=True,
        )

    #----------------------------------------------------------------------
    # Default values
    #----------------------------------------------------------------------

    def _bar_plot_default(self):

        # Default data
        idx = np.array([1, 2, 3, 4, 5])
        vals = np.array([2, 4, 7, 4, 3])

        # Mappers
        index = ArrayDataSource(idx)
        index_range = DataRange1D(index, low=0.5, high=5.5)
        index_mapper = LinearMapper(range=index_range)

        value = ArrayDataSource(vals)
        value_range = DataRange1D(value, low=0)
        value_mapper = LinearMapper(range=value_range)

        # The bar plot
        plot = BarPlot(index=index, value=value,
                       value_mapper=value_mapper,
                       index_mapper=index_mapper,
                       line_color="black",
                       fill_color="cornflowerblue",
                       bgcolor="white",
                       bar_width=self.bar_width,
                       line_width=self.line_width,
                       )
        return plot


    #----------------------------------------------------------------------
    # Trait change handlers
    #----------------------------------------------------------------------

    def _line_color_alpha_changed(self):
        alpha = self.line_color_alpha
        color = self.bar_plot.line_color_
        self.bar_plot.line_color = color[:3] + (alpha,)

    def _fill_color_alpha_changed(self):
        alpha = self.fill_color_alpha
        color = self.bar_plot.fill_color_
        self.bar_plot.fill_color = color[:3] + (alpha,)

    def _alpha_changed(self):
        self.bar_plot.alpha = self.alpha

    def _bar_width_changed(self):
        self.bar_plot.bar_width = self.bar_width

    def _line_width_changed(self):
        self.bar_plot.line_width = self.line_width

demo = BarPlotDemo()

if __name__ == "__main__":
    demo.configure_traits()
