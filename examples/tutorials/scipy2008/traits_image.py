
from numpy import linspace, meshgrid, exp

from chaco.api import ArrayPlotData, Plot, jet
from enable.component_editor import ComponentEditor
from traits.api import Enum, HasTraits, Instance
from traitsui.api import Group, Item, View

class ImagePlotTraits(HasTraits):

    plot = Instance(Plot)
    origin = Enum("bottom left", "top left", "bottom right", "top right")

    traits_view = View(
                    Group(
                        Item('origin', label="Data origin"),
                        Item('plot', editor=ComponentEditor(), show_label=False),
                        orientation = "vertical"),
                    width=600, height=600, resizable=True,
                    title="Chaco Plot"
                    )

    def __init__(self):
        # Create the data and the PlotData object.  For a 2D plot, we need to
        # take the row of X points and Y points and create a grid from them
        # using meshgrid().
        x = linspace(0, 8, 50)
        y = linspace(0, 6, 50)
        xgrid, ygrid = meshgrid(x, y)
        z = exp(-(xgrid*xgrid + ygrid*ygrid) / 100)
        plotdata = ArrayPlotData(imagedata = z)
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        # Create an image plot in the Plot
        self.renderer = plot.img_plot("imagedata", name="plot1", colormap=jet)[0]
        self.plot = plot
        return

    def _origin_changed(self):
        self.renderer.origin = self.origin
        self.plot.request_redraw()

#===============================================================================
# demo object that is used by the demo.py application.
#===============================================================================
demo = ImagePlotTraits()

if __name__ == "__main__":
    demo.configure_traits()

