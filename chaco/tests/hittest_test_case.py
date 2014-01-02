"""
Test cases for the LinePlot's hittest() function
"""

import unittest
from numpy import arange, array, linalg
from chaco.api import (ArrayDataSource, ArrayPlotData,
                       Plot, LinearMapper, DataRange1D)

class HittestTestCase(unittest.TestCase):
    def make_plot(self, orientation):
        # make some data points
        x = arange(3)
        x = ArrayDataSource(x, sort_order="ascending")
        y = array([2,0,1])

        # Plot the data
        pd = ArrayPlotData(x=x, y=y)

        plot = Plot(pd, orientation=orientation)
        line_plot = plot.plot(("x", "y"))[0]

        # Construct a fake screen space for the plots
        # otherwise would need to actually display the plots to get this
        index_mapper = LinearMapper(data_range=DataRange1D(low=0,high=2),
                                    high_pos=380, low_pos=20)
        value_mapper = LinearMapper(data_range=DataRange1D(low=0,high=2),
                                    high_pos=380, low_pos=20)
        plot.index_mapper = index_mapper
        plot.value_mapper = value_mapper
        line_plot.index_mapper = index_mapper
        line_plot.value_mapper = value_mapper

        return  plot, line_plot

    def test_horizontal(self):
        plot, line_plot = self.make_plot("h")

        self._test_plot(plot, line_plot, point=[0.5,1])
        self._test_plot(plot, line_plot, point=[1,0])

    def test_vertical(self):
        plot, line_plot = self.make_plot("v")

        self._test_plot(plot, line_plot, point=[0.5,1])
        self._test_plot(plot, line_plot, point=[1,0])

    def _test_plot(self, plot, line_plot, point):
        threshold = 2 # In pixels

        screen_pt = plot.map_screen(point).flatten()
        result = line_plot.hittest(screen_pt, threshold=threshold)

        self.assertTrue(result is not None)

        # Check that the result is close by threshold in screenspace
        screen_result = plot.map_screen(result)

        self.assertTrue(linalg.norm(screen_pt - screen_result) < threshold)

        # check the return_distance = True case:
        x, y, d = line_plot.hittest(screen_pt, threshold=threshold,
                                    return_distance=True)
        self.assertEqual(x, result[0])
        self.assertEqual(y, result[1])
        self.assertTrue(d < threshold)

if __name__ == '__main__':
    import nose
    nose.run()
