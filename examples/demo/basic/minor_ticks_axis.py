import numpy as np

from chaco.api import ArrayPlotData, MinorPlotAxis, Plot
from chaco.tools.api import PanTool, ZoomTool
from enable.api import ComponentEditor
from traits.api import Instance, HasTraits
from traitsui.api import UItem, View


class MinorTickDemo(HasTraits):
    """A plot with minor tick labels."""

    plot = Instance(Plot)

    view = View(UItem("plot", editor=ComponentEditor()), resizable=True)

    def _plot_default(self):
        x = np.linspace(0, 2 * np.pi)
        plotdata = ArrayPlotData(x=x, y=np.sin(x))
        plot = Plot(plotdata)
        plot.plot(("x", "y"), type="line")

        plot.tools.append(ZoomTool(plot))
        plot.tools.append(PanTool(plot))

        # A standard minor plot axis.
        xminor = MinorPlotAxis(
            orientation="bottom",
            mapper=plot.x_mapper,
            component=plot,
        )
        plot.underlays.append(xminor)

        # A customized minor plot axis.
        yminor = MinorPlotAxis(
            orientation="left",
            mapper=plot.y_mapper,
            component=plot,
            tick_color="red",
            tick_weight=2,
            tick_in=4,
            tick_out=2,
        )

        # To avoid the (heavily customized) minor axis painting over the major
        # axis, we insert it at the front of the underlays array, so that it
        # gets drawn ahead of everything else.
        plot.underlays.insert(0, yminor)

        # Customizations for the y-major axis to make it stand out a little.
        ymajor = plot.y_axis
        ymajor.tick_color = "blue"
        ymajor.tick_weight = 3
        ymajor.tick_in = 7
        ymajor.tick_out = 3

        return plot


if __name__ == "__main__":
    demo = MinorTickDemo()
    demo.configure_traits()
