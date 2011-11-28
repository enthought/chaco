from chaco.api import Plot, ArrayPlotData

from traits.api import HasTraits, Instance
from enable.component_editor import ComponentEditor
from traitsui.api import Item, View

import numpy as np


class PlotViewer(HasTraits):
    plot = Instance(Plot)
    traits_view = View(Item('plot', editor=ComponentEditor()))


def test_bounds_2d_case():
    # test for bug: contour and image plots should support the case where
    # xbounds and ybounds are 2d arrays resulting from meshgrids

    xs = np.linspace(-10,10,200)
    ys = np.linspace(-10,10,400)
    x, y = np.meshgrid(xs,ys)
    z = x + y

    plotdata = ArrayPlotData()
    plotdata.set_data("z", z)

    plot = Plot(plotdata)
    plot.contour_plot("z", xbounds=x, ybounds=y)

    # try to display it, that's when the exception is raised
    pv = PlotViewer(plot=plot)
    pv.edit_traits()


if __name__ == '__main__':
    import nose
    nose.main()
