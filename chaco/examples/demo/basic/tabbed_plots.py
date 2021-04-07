"""
Tabbed plots with linked (shared) data ranges

Shows how to place plots in separate tabs. Also shows how two plots can
dynamically display the same range of data, so that a zoom or pan in one
plot will automatically be shown in the other.

In this example, the top panel plots a sin function. The bottom panel contains 
two tabs, plotting a tan function and a mixed trig function respectively.

The three plots are linked. The sin and mixed plots share both x- and y-axis
data ranges. The tan plot shares only its x-axis with the other two. 

Mousewheel zooms in or out. Left-mouse-drag pans. 
Typing "z", then left-mouse-drag, zooms to a specified region.

If you zoom or pan one plot, you will see changes in one or both axis ranges
of the other plots.
"""

from numpy import linspace, pi, sin, tan, cos

from traits.api import HasTraits, Instance
from traitsui.api import UItem, Tabbed, View, VGroup

from chaco.api import Plot, AbstractPlotData, ArrayPlotData
from chaco.tools.api import PanTool, ZoomTool
from enable.component_editor import ComponentEditor


class TabbedPlots(HasTraits):

    data = Instance(AbstractPlotData)

    plot_sin = Instance(Plot)
    plot_tan = Instance(Plot)
    plot_mixed = Instance(Plot)

    view = View(
        VGroup(
            # UItem is an unlabeled item
            UItem("plot_sin", editor=ComponentEditor(), dock="tab"),
            Tabbed(
                UItem("plot_tan", editor=ComponentEditor(), dock="tab"),
                UItem("plot_mixed", editor=ComponentEditor(), dock="tab"),
            ),
        ),
        title="Tabbed plots with shared data ranges",
        width=0.67,
        height=0.4,
        resizable=True,
    )

    def create_plot(self, data, name, color):
        p = Plot(self.data)
        p.plot(data, name=name, color=color)
        p.tools.append(PanTool(p))
        p.overlays.append(ZoomTool(p))
        return p

    def create_plots(self):
        self.plot_sin = self.create_plot(("x", "ysin"), "sin plot", "red")
        self.plot_tan = self.create_plot(("x", "ytan"), "tan plot", "blue")
        self.plot_mixed = self.create_plot(
            ("x", "ymix"), "mixed plot", "green"
        )

        # The mixed plot will share both x and y ranges with the sin plot.
        # This 2d range is a single object shared by both plots. For its
        # initial value, we will use the range of the mixed plot, whose y-range
        # is auto-set to slightly larger than that of the sin plot.
        self.plot_sin.range2d = self.plot_mixed.range2d

        # The sin & mixed plots will share only their x range with the tan plot.
        # Again, this x-axis range is a single object shared by all 3 plots.
        # It is contained within the 2d range shared by the sin and mixed plots.
        # (The independent variable, in this case x, is called "index" in chaco.
        # The dependent variable is called "value".)
        self.plot_tan.index_range = self.plot_sin.index_range

    def _data_changed(self):
        self.create_plots()


# ===============================================================================
# # demo object that is used by the demo.py application.
# ===============================================================================
x = linspace(-2 * pi, 2 * pi, 100)
demo = TabbedPlots(
    data=ArrayPlotData(
        x=x, ysin=sin(x), ytan=tan(x), ymix=sin(x) ** 2 + cos(x)
    )
)

if __name__ == "__main__":
    demo.configure_traits()
