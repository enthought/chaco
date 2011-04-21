
from numpy import linspace, sin
from enthought.chaco.api import ArrayPlotData, Plot
from enthought.enable.component_editor import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View

class LinePlot(HasTraits):

    plot = Instance(Plot)

    traits_view = View(
            Item('plot', editor=ComponentEditor(),
                 show_label=False),
            width=500, height=500,
            resizable=True,
            title = "Chaco Plot")

    def __init__(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        # Create a line plot in the Plot
        plot.plot(("x", "y"), type="line", color="blue")
        # Set the title
        plot.title = "sin(x) * x^3"
        # Assign it to our self.plot attribute
        self.plot = plot

#===============================================================================
# demo object that is used by the demo.py application.
#===============================================================================
demo=LinePlot()
if __name__ == "__main__":
    demo.configure_traits()

