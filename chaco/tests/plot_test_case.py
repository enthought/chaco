import unittest

from chaco.api import Plot


class PlotTestCase(unittest.TestCase):

    def test_empty(self):
        plot = Plot()
        self.assertEqual(plot.orientation, "h")
        self.assertEqual(plot.index_scale, "linear")
        self.assertEqual(plot.bgcolor, "white")
        self.assertEqual(plot.overlay_border, True)

        self.assertEqual(plot.range2d.x_range, plot.index_range)
        self.assertEqual(plot.range2d.y_range, plot.value_range)
        self.assertEqual(plot.bgcolor, "white")

    def test_bgcolor(self):
        """ Test setting background color """
        color = 'blue'
        plot = Plot(bgcolor=color)
        self.assertEqual(plot.bgcolor, color)
        color = (0,0,0,0)
        plot = Plot(bgcolor=color)
        self.assertEqual(plot.bgcolor, color)


if __name__ == '__main__':
    unittest.main()

