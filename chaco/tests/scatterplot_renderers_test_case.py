import unittest

from numpy import alltrue
from enable.compiled_path import CompiledPath

# Chaco imports
from chaco.api import create_scatter_plot, PlotGraphicsContext


class DrawScatterplotCase(unittest.TestCase):
    def test_scatter_fast(self):
        """ Coverage test to check basic case works """
        size = (50,50)
        scatterplot = create_scatter_plot(
            data=[range(10), range(10)],
            border_visible=False,
        )
        scatterplot.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(scatterplot)
        actual = gc.bmp_array[:,:,:]
        #gc.save('scatter.png')
        assert(not alltrue(actual == 255))

    def test_scatter_circle(self):
        """ Coverage test to check circles work """
        size = (50,50)
        scatterplot = create_scatter_plot(
            data=[range(10), range(10)],
            marker="circle",
            border_visible=False,
        )
        scatterplot.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(scatterplot)
        actual = gc.bmp_array[:,:,:]
        #gc.save('scatter.png')
        assert(not alltrue(actual == 255))

    def test_scatter_custom(self):
        """ Coverage test to check custom markers work """
        # build path
        path = CompiledPath()
        path.move_to(-5,-5)
        path.line_to(5, 5)
        path.line_to(5, -5)
        path.line_to(-5, 5)
        path.line_to(-5, -5)

        size = (50,50)
        scatterplot = create_scatter_plot(
            data=[range(10), range(10)],
            marker='custom',
            border_visible=False,
        )
        scatterplot.custom_symbol = path
        scatterplot.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(scatterplot)
        actual = gc.bmp_array[:,:,:]
        #gc.save('scatter.png')
        assert(not alltrue(actual == 255))

    def test_scatter_slow(self):
        """ Coverage test to check multiple marker size works """
        size = (50,50)
        scatterplot = create_scatter_plot(
            data=[range(10), range(10)],
            border_visible=False,
            marker_size=range(1,11),
        )
        scatterplot.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(scatterplot)
        actual = gc.bmp_array[:,:,:]
        #gc.save('scatter.png')
        assert(not alltrue(actual == 255))


if __name__ == "__main__":
    unittest.main()
