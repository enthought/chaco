from numpy import linspace
from scipy.special import jn

from chaco.api import ArrayPlotData, Plot, OverlayPlotContainer
from chaco.tools.api import ZoomTool, PanTool
from enable.api import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View


class OverlayContainerExample(HasTraits):

    plot = Instance(OverlayPlotContainer)

    traits_view = View(
        Item("plot", editor=ComponentEditor(), show_label=False),
        width=800,
        height=600,
        resizable=True,
    )

    def _plot_default(self):
        # Create data
        x = linspace(-5, 15.0, 100)
        y = jn(3, x)
        pd = ArrayPlotData(index=x, value=y)

        zoomable_plot = Plot(pd)
        zoomable_plot.plot(
            ("index", "value"), name="external", color="red", line_width=3
        )

        # Attach tools to the plot
        zoom = ZoomTool(
            component=zoomable_plot, tool_mode="box", always_on=False
        )
        zoomable_plot.overlays.append(zoom)
        zoomable_plot.tools.append(PanTool(zoomable_plot))

        # Create a second inset plot, not resizable, not zoom-able
        inset_plot = Plot(pd)
        inset_plot.plot(("index", "value"), color="blue")
        inset_plot.resizable = ""
        inset_plot.bounds = [250, 150]
        inset_plot.position = [450, 350]
        inset_plot.border_visible = True

        # Create a container and add our plots
        container = OverlayPlotContainer()
        container.add(zoomable_plot)
        container.add(inset_plot)
        return container


if __name__ == "__main__":
    demo = OverlayContainerExample()
    demo.configure_traits()
