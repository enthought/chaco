import unittest

import numpy as np

from enable.api import ComponentEditor
from enable.testing import EnableTestAssistant
from traits.api import HasTraits, Instance
from traitsui.api import Item, View

from chaco.api import ArrayPlotData, DataLabel, Plot
from chaco.tools.api import DataLabelTool

IMAGE = np.random.random_integers(0, 255, size=(100, 200)).astype(np.uint8)
RGB = np.dstack([IMAGE] * 3)


class TestDataLabelTool(unittest.TestCase, EnableTestAssistant):

    # regression test for enthought/chaco#550
    def test_use_with_2d_plot(self):
        class Test2DPlot(HasTraits):
            plot = Instance(Plot)

            traits_view = View(
                Item('plot', editor=ComponentEditor(), show_label=False),
                width=500,
                height=500,
                resizable=True
            )

            def _plot_default(self):
                pd = ArrayPlotData(image=RGB)
                plot = Plot(pd)
                self.renderer = plot.img_plot('image')[0]

                label = DataLabel(
                    component=self.renderer,
                    data_point=(25, 12)
                )
                plot.overlays.append(label)
                tool = DataLabelTool(label)
                label.tools.append(tool)
                return plot

        test_2d_plot = Test2DPlot()
        # should not fail
        self.press_move_release(
            test_2d_plot.plot,
            [(0, 0), (200, 200), (300, 300)],
        )

    def test_use_with_xy_plot(self):
        class TestXYPlot(HasTraits):
            plot = Instance(Plot)

            traits_view = View(
                Item('plot', editor=ComponentEditor(), show_label=False),
                width=500,
                height=500,
                resizable=True
            )

            def _plot_default(self):
                values = np.arange(10)
                plotdata = ArrayPlotData(x=values, y=values)

                plot = Plot(plotdata)
                self.renderer = plot.plot(
                    ("x", "y"), type="line", color="blue"
                )[0]

                label = DataLabel(
                    component=self.renderer,
                    data_point=(5, 5)
                )
                plot.overlays.append(label)
                tool = DataLabelTool(label)
                label.tools.append(tool)
                return plot

        test_xy_plot = TestXYPlot()
        # should not fail
        self.press_move_release(
            test_xy_plot.plot,
            [(0, 0), (200, 200), (300, 300)],
        )
