from chaco.api import ArrayPlotData, HPlotContainer, Plot
from enable.component_editor import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View

from numpy.random import random

N_POINTS = 100

class ColorbarExample(HasTraits):

    plot = Instance(HPlotContainer)

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False),
                       width=1000, height=600, resizable=True)

    def __init__(self):
        # Create some data
        x = random(N_POINTS)
        y = random(N_POINTS)
        color = exp(-(x**2 + y**2))

        # Create a plot data object and give it this data
        data = ArrayPlotData(index=x, value=y, color=color)

        # Create the plot
        plot = Plot(data)
        plot.plot(("index", "value", "color"),
                  type="cmap_scatter")

if __name__ == "__main__":
    demo = ColorbarExample()
    demo.configure_traits()


# Create the colorbar, handing in the appropriate range and colormap
colorbar = create_colorbar(plot.color_mapper)
colorbar.plot = cmap_renderer
colorbar.padding_top = plot.padding_top
colorbar.padding_bottom = plot.padding_bottom

# Create a container to position the plot and the colorbar side-by-side
container = HPlotContainer(use_backbuffer = True)
container.add(plot)
container.add(colorbar)
container.bgcolor = "lightgray"
return container
