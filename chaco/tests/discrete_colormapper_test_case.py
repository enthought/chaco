import unittest

from numpy import array, empty, uint8
from numpy.testing import assert_array_almost_equal, assert_array_equal

from chaco.api import DiscreteColorMapper


class DiscreteColormapTestCase(unittest.TestCase):

    def setUp(self):
        gray_data = empty(shape=(5, 3))
        gray_data[:] = array([0.0, 0.25, 0.5, 0.75, 1.0]).reshape(5, 1)

        self.colormap = DiscreteColorMapper.from_palette_array(gray_data)

    def test_simple_map(self):
        a = array([0, 2, 3])
        b = self.colormap.map_screen(a)

        self.assertEqual(b.shape, (3, 4))
        for i in range(3):
            assert_array_almost_equal(b[:, i], array([0.0, 0.5, 0.75]))
        assert_array_almost_equal(b[:, 3], [1, 1, 1])

    def test_color_space_rgb(self):
        self.colormap.color_depth = 'rgb'
        a = array([0, 2, 3])
        b = self.colormap.map_screen(a)

        self.assertEqual(b.shape, (3, 3))
        for i in range(3):
            assert_array_almost_equal(b[:, i], array([0.0, 0.5, 0.75]))

    def test_map_uint8(self):
        self.colormap.color_depth = 'rgb'
        a = array([0, 2, 3])
        b = self.colormap.map_uint8(a)

        self.assertEqual(b.shape, (3, 3))
        self.assertEqual(b.dtype, uint8)
        for i in range(3):
            assert_array_almost_equal(b[:, i], array([0, 128, 192]))

    def test_map_uint8_rgb(self):
        a = array([0, 2, 3])
        b = self.colormap.map_uint8(a)

        self.assertEqual(b.shape, (3, 4))
        self.assertEqual(b.dtype, uint8)
        for i in range(3):
            assert_array_almost_equal(b[:, i], array([0, 128, 192]))
        assert_array_almost_equal(b[:, 3], [255, 255, 255])

    def test_map_index(self):
        self.colormap.color_depth = 'rgb'
        a = array([0, 2, 3])
        b = self.colormap.map_index(a)

        self.assertEqual(b.shape, (3,))
        self.assertEqual(b.dtype, int)
        assert_array_equal(b, array([0, 2, 3]))

    def test_alpha_palette(self):
        gray_data = empty(shape=(5, 4))
        gray_data[:] = array([0.0, 0.25, 0.5, 0.75, 1.0]).reshape(5, 1)
        self.colormap = DiscreteColorMapper.from_palette_array(gray_data)
        a = array([0, 2, 3])
        b = self.colormap.map_screen(a)

        self.assertEqual(b.shape, (3, 4))
        for i in range(4):
            assert_array_almost_equal(b[:, i], array([0.0, 0.5, 0.75]))

    def test_alpha_palette_rgb(self):
        gray_data = empty(shape=(5, 4))
        gray_data[:] = array([0.0, 0.25, 0.5, 0.75, 1.0]).reshape(5, 1)
        self.colormap = DiscreteColorMapper.from_palette_array(
            gray_data, color_depth='rgb')
        a = array([0, 2, 3])
        b = self.colormap.map_screen(a)

        self.assertEqual(b.shape, (3, 3))
        for i in range(3):
            assert_array_almost_equal(b[:, i], array([0.0, 0.5, 0.75]))

    def test_alpha_palette_map_uint8(self):
        gray_data = empty(shape=(5, 4))
        gray_data[:] = array([0.0, 0.25, 0.5, 0.75, 1.0]).reshape(5, 1)
        self.colormap = DiscreteColorMapper.from_palette_array(gray_data)
        a = array([0, 2, 3])
        b = self.colormap.map_uint8(a)

        self.assertEqual(b.shape, (3, 4))
        self.assertEqual(b.dtype, uint8)
        for i in range(4):
            assert_array_almost_equal(b[:, i], array([0, 128, 192]))

    def test_alpha_palette_map_uint8_rgb(self):
        gray_data = empty(shape=(5, 4))
        gray_data[:] = array([0.0, 0.25, 0.5, 0.75, 1.0]).reshape(5, 1)
        self.colormap = DiscreteColorMapper.from_palette_array(
            gray_data, color_depth='rgb')
        a = array([0, 2, 3])
        b = self.colormap.map_uint8(a)

        self.assertEqual(b.shape, (3, 3))
        self.assertEqual(b.dtype, uint8)
        for i in range(3):
            assert_array_almost_equal(b[:, i], array([0, 128, 192]))

    def test_from_colormap(self):
        from chaco.color_mapper import ColorMapper

        def colormap_function(range, **traits):
            """ Typical colormap generator """
            _gray_data =  {'red':   [(0., 0, 0), (1., 1.0, 1.0)],
                           'green': [(0., 0, 0), (1., 1.0, 1.0)],
                           'blue':  [(0., 0, 0), (1., 1.0, 1.0)]}
            return ColorMapper.from_segment_map(_gray_data, range=range,
                                                **traits)
        self.colormap = DiscreteColorMapper.from_colormap(
            colormap_function, steps=5)

        gray_data = empty(shape=(5, 4))
        gray_data[:] = array([0.0, 0.25, 0.5, 0.75, 1.0]).reshape(5, 1)
        self.colormap = DiscreteColorMapper.from_palette_array(gray_data)
        a = array([0, 2, 3])
        b = self.colormap.map_screen(a)

        self.assertEqual(b.shape, (3, 4))
        for i in range(4):
            assert_array_almost_equal(b[:, i], array([0.0, 0.5, 0.75]))

if __name__ == '__main__':
    import nose
    nose.run()
