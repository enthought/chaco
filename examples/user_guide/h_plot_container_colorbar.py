from chaco.api import ArrayPlotData, HPlotContainer, Plot, viridis, ColorBar
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View

import numpy as np
from chaco.linear_mapper import LinearMapper

N_POINTS = 100


class ColorbarExample(HasTraits):

    plot = Instance(HPlotContainer)

    traits_view = View(
        Item("plot", editor=ComponentEditor(), show_label=False),
        width=600,
        height=600,
        resizable=True,
    )

    def __init__(self):
        # Create some data
        x = np.random.random(N_POINTS)
        y = np.random.random(N_POINTS)
        color = np.exp(-(x ** 2 + y ** 2))

        # Create a plot data object and give it this data
        data = ArrayPlotData(index=x, value=y, color=color)

        # Create the plot
        plot = Plot(data)
        plot.plot(
            ("index", "value", "color"),
            type="cmap_scatter",
            color_mapper=viridis,
        )

        # Create the colorbar, handing in the appropriate range and colormap
        colormap = plot.color_mapper
        colorbar = ColorBar(
            index_mapper=LinearMapper(range=colormap.range),
            color_mapper=colormap,
            orientation="v",
            resizable="v",
            width=30,
            padding=20,
        )

        colorbar.padding_top = plot.padding_top
        colorbar.padding_bottom = plot.padding_bottom

        # Create a container to position the plot and the colorbar side-by-side
        container = HPlotContainer(plot, colorbar)
        self.plot = container


if __name__ == "__main__":
    demo = ColorbarExample()
    demo.configure_traits()
