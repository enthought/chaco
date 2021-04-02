import unittest

from numpy import allclose, array, ravel

from chaco.api import ArrayDataSource, ColorMapper, DataRange1D


class LinearSegmentedColormapTestCase(unittest.TestCase):

    def setUp(self):
        """ Set up called before each test case. """

        _gray_data =  {'red':   [(0., 0, 0), (1., 1.0, 1.0)],
                       'green': [(0., 0, 0), (1., 1.0, 1.0)],
                       'blue':  [(0., 0, 0), (1., 1.0, 1.0)]}

        self.colormap = ColorMapper.from_segment_map(_gray_data)
        self.colormap.range = DataRange1D()

    def test_simple_map(self):

        a = ArrayDataSource(array([0.0, 0.5, 1.0]))
        self.colormap.range.add(a)
        b = self.colormap.map_screen(a.get_data())
        self.colormap.range.remove(a)

        expected = array([0.0, 0.5, 1.0])

        close = allclose(ravel(b[:,:1]), expected, atol=0.02)
        self.assertTrue(close,
            "Simple map failed.  Expected %s.  Got %s" % (expected, b[:,:1]))

    def test_change_min_max(self):
        """ Test that changing min_value and max_value does not break map. """

        datarange = self.colormap.range

        # Perform a dummy mapping.
        a = ArrayDataSource(array([0.0, 0.5, 1.0]))
        datarange.add(a)
        b = self.colormap.map_screen(a.get_data())
        datarange.remove(a)

        # Update the min_value.
        datarange.low = -1.0

        # Test that the map still works.
        a = ArrayDataSource(array([-1.0, 0.0, 1.0]))
        datarange.add(a)
        b = self.colormap.map_screen(a.get_data())
        datarange.remove(a)
        expected = array([0.0, 0.5, 1.0])

        close = allclose(ravel(b[:,:1]), expected, atol=0.02)
        self.assertTrue(close,
            "Changing min value broke map.  Expected %s.  Got %s" % (expected, b[:,:1]))

        # Update the max_value.
        datarange.high = 0.0
        # Test that the map still works.
        a = ArrayDataSource(array([-1.0, -0.5, 0.0]))
        datarange.add(a)
        b = self.colormap.map_screen(a.get_data())
        datarange.remove(a)
        expected = array([0.0, 0.5, 1.0])

        close = allclose(ravel(b[:,:1]), expected, atol=0.02)
        self.assertTrue(close,
            "Changing min value broke map.  Expected %s.  Got %s" % (expected, b[:,:1]))

    def test_array_factory(self):
        """ Test that the array factory creates valid colormap. """

        colors = array([[0.0,0.0,0.0], [1.0,1.0,1.0]])
        cm = ColorMapper.from_palette_array(colors)
        cm.range = DataRange1D()

        ar = ArrayDataSource(array([0.0, 0.5, 1.0]))
        cm.range.add(ar)
        b = cm.map_screen(ar.get_data())
        cm.range.remove(ar)

        expected = array([0.0, 0.5, 1.0])

        self.assertTrue(allclose(ravel(b[:,:1]), expected, atol=0.02),
            "Array factory failed.  Expected %s.  Got %s" % (expected, b[:,:1]))

    def test_alpha_palette(self):
        """ Create a colormap with a varying alpha channel from a palette array.
        """
        cm = ColorMapper.from_palette_array([[0.0,0.0,0.0,0.5],[1.0,1.0,1.0,1.0]])
        sd = {'alpha': [(0.0, 0.5, 0.5), (1.0, 1.0, 1.0)],
              'blue': [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
              'green': [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
              'red': [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)]}
        assert cm._segmentdata == sd

    def test_alpha_segment_data(self):
        """ Create a colormap with a varying alpha channel from segment data.
        """
        sd = {'alpha': [(0.0, 0.5, 0.5), (1.0, 1.0, 1.0)],
              'blue': [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
              'green': [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
              'red': [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)]}
        cm = ColorMapper.from_segment_map(sd)
        assert cm._segmentdata == sd

    def test_no_alpha(self):
        """ Check that the defaults when no alpha is specified are correct.
        """
        sd = {'alpha': [(0.0, 1.0, 1.0), (1.0, 1.0, 1.0)],
              'blue': [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
              'green': [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
              'red': [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)]}
        assert self.colormap._segmentdata == sd


##     def test_no_interpolation(self):
##         grayscale_colors = array([[0.0,0.0,0.0,1.0], [1.0, 1.0, 1.0, 1.0]])
##         grayscale_bins = array([0.0, 1.0])
##         grayscale_steps = array([1])

##         colormap = LinearSegmentedColormap(
##             grayscale_colors, grayscale_bins, grayscale_steps
##         )

##         a = array([0.0, 0.25, 0.75, 1.0])
##         b = colormap.map_array(a)
##         result = ravel(b[:,:1])
##         expected = array([0.0, 0.0, 1.0, 1.0])

##         close = allclose(result, expected, atol=0.02)
##         self.assert_(close,
##             "Map with no interpolation broken.  Expected %s.  Got %s" % (expected, result))

##     def test_value_bands(self):

##         grayscale_colors = array([[0.0,0.0,0.0,1.0], [1.0, 1.0, 1.0, 1.0]])
##         grayscale_bins = array([0.0, 1.0])
##         grayscale_steps = array([1])

##         colormap = LinearSegmentedColormap(
##             grayscale_colors, grayscale_bins, grayscale_steps
##         )

##         colormap._recalculate()

##         print '**************', colormap._color_bands, colormap._value_bands
