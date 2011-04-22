
from numpy import linspace, meshgrid, exp

from enthought.chaco.api import ArrayPlotData, Plot, jet
from enable.component_editor import ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, View

class ImagePlot(HasTraits):

    plot = Instance(Plot)

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False),
                       width=600, height=600,
                       resizable=True,
                       title="Chaco Plot")

    def __init__(self):
        # Create the data and the PlotData object.  For a 2D plot, we need to
        # take the row of X points and Y points and create a grid from them
        # using meshgrid().
        x = linspace(0, 10, 50)
        y = linspace(0, 5, 50)
        xgrid, ygrid = meshgrid(x, y)
        z = exp(-(xgrid*xgrid + ygrid*ygrid) / 100)
        plotdata = ArrayPlotData(imagedata = z)
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        # Create a line plot in the Plot
        plot.img_plot("imagedata", colormap=jet)
        self.plot = plot

#===============================================================================
# demo object that is used by the demo.py application.
#===============================================================================
demo = ImagePlot()
if __name__ == "__main__":
    demo.configure_traits()

