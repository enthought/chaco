
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import mock

import numpy

from enable.api import AbstractWindow
from chaco.cmap_image_plot import CMapImagePlot
from chaco.data_range_1d import DataRange1D
from chaco.data_range_2d import DataRange2D
from chaco.grid_data_source import GridDataSource
from chaco.grid_mapper import GridMapper
from chaco.image_data import ImageData
from chaco.default_colormaps import Spectral

class TestCMapImagePlot(unittest.TestCase):

    def test_redraw_on_color_mapper_update(self):
        # regression check for https://github.com/enthought/chaco/issues/220
        npoints = 200

        xs = numpy.linspace(-2 * numpy.pi, +2 * numpy.pi, npoints)
        ys = numpy.linspace(-1.5*numpy.pi, +1.5*numpy.pi, npoints)
        x, y = numpy.meshgrid(xs, ys)
        z = y * x

        index = GridDataSource(xdata=xs, ydata=ys)
        index_mapper = GridMapper(range=DataRange2D(index))

        color_source = ImageData(data=z, value_depth=1)
        color_mapper = Spectral(DataRange1D(color_source))

        cmap_plot = CMapImagePlot(
            index=index,
            index_mapper=index_mapper,
            value=color_source,
            value_mapper=color_mapper,
        )
        cmap_plot._window = window = mock.Mock(spec=AbstractWindow)

        #when
        cmap_plot.color_mapper.updated = True

        # Then
        window.redraw.assert_called_once_with()

if __name__ == "__main__":
    unittest.main()
