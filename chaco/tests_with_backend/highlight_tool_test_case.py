from traits.api import HasTraits, Instance
from traitsui.api import Item, View
from enable.component_editor import ComponentEditor

from chaco.api import Plot, ArrayPlotData
from chaco.tools.highlight_tool import HighlightTool

import numpy as np

import nose


class PlotViewer(HasTraits):
    plot = Instance(Plot)
    traits_view = View(Item('plot', editor=ComponentEditor()))


class MockEvent(HasTraits):
    pass


def test_highlight_on_log_plot():
    # test for bug: the highlight tool raises an exception when used on
    # a loglog plot

    x = np.linspace(1, 15, 200)

    plotdata = ArrayPlotData()
    plotdata.set_data("x", x)
    plotdata.set_data("y", x*x)

    plot = Plot(plotdata)
    plot.plot(("x", "y"), index_scale='log', value_scale='log')

    # necessary for the machinery involved in _find_curve
    plot.datasources["x"].sort_order = 'ascending'
    plot.datasources["y"].sort_order = 'ascending'

    # add the highlight tool
    htool = HighlightTool(plot, threshold=20.)
    plot.tools.append(htool)

    # we create a view of the plot so that the screen bounds are set
    pv = PlotViewer(plot=plot)
    pv.edit_traits()

    # this should not raise an exception
    event = MockEvent(x=170., y=60.)
    htool._find_curve(plot.plots['plot0'], event)


if __name__ == '__main__':
    nose.main()
