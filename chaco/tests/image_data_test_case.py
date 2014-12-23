"""
Test of ImageData behavior.
"""

import os

import unittest2 as unittest
from numpy import arange, swapaxes
from numpy.testing import assert_array_equal
from pkg_resources import resource_filename

from chaco.api import ImageData
from traits.testing.unittest_tools import UnittestTools


data_dir = resource_filename('chaco.tests', 'data')


class ImageDataTestCase(UnittestTools, unittest.TestCase):

    def setUp(self):
        self.myarray = arange(15).reshape(5, 3, 1)
        self.data_source = ImageData(data=self.myarray)

    def test_init_defaults(self):
        data_source = ImageData()
        assert_array_equal(data_source.data, [])

        # this isn't right -
        #self.assertEqual(data_source.value_dimension, "scalar")
        #self.assertEqual(data_source.image_dimension, "image")

    def test_basic_setup(self):
        assert_array_equal(self.myarray, self.data_source.data)
        #self.assertEqual(self.data_source.value_dimension, "scalar")
        self.assertFalse(self.data_source.is_masked())

    def test_set_data(self):
        new_array = arange(0, 30, 2).reshape(5, 3, 1)

        with self.assertTraitChanges(self.data_source, 'data_changed', count=1):
            self.data_source.set_data(new_array)

        assert_array_equal(new_array, self.data_source.data)
        self.assertEqual(self.data_source.get_bounds(), (0, 28))

    def test_get_data(self):
        assert_array_equal(self.myarray, self.data_source.get_data())

    def test_get_data_no_data(self):
        data_source = ImageData()

        self.assertIsNone(data_source.get_data())

    def test_get_data_transposed(self):
        myarray = arange(15).reshape(5, 3, 1)
        data_source = ImageData(data=myarray, transposed=True)

        assert_array_equal(swapaxes(myarray, 0, 1), self.data_source.get_data())

    def test_get_data_mask(self):
        # XXX this is probably not the right thing
        with self.assertRaises(NotImplementedError):
            data, mask = self.data_source.get_data_mask()

    def test_get_data_mask_no_data(self):
        data_source = ImageData()

        # XXX this is probably not the right thing
        with self.assertRaises(NotImplementedError):
            data, mask = data_source.get_data_mask()

    def test_bounds(self):
        bounds = self.data_source.get_bounds()
        self.assertEqual(bounds, (0, 14))

    @unittest.skip('test_bounds_empty() fails in this case')
    def test_bounds_empty(self):
        data_source = ImageData()
        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (0, 0))

    def test_data_size(self):
        self.assertEqual(15, self.data_source.get_size())

    def test_data_size_no_data(self):
        data_source = ImageData()
        self.assertEqual(0, data_source.get_size())

    def test_get_width(self):
        self.assertEqual(3, self.data_source.get_width())

    def test_get_width_transposed(self):
        myarray = arange(15).reshape(5, 3)
        data_source = ImageData(data=myarray, transposed=True)

        self.assertEqual(5, data_source.get_width())

    def test_get_height(self):
        self.assertEqual(5, self.data_source.get_height())

    def test_get_height_transposed(self):
        myarray = arange(15).reshape(5, 3, 1)
        data_source = ImageData(data=myarray, transposed=True)

        self.assertEqual(3, data_source.get_height())

    def test_array_bounds(self):
        self.assertEqual(((0, 3), (0, 5)), self.data_source.get_array_bounds())

    def test_array_bounds_transposed(self):
        myarray = arange(15).reshape(5, 3, 1)
        data_source = ImageData(data=myarray, transposed=True)

        self.assertEqual(((0, 5), (0, 3)), data_source.get_array_bounds())

    def test_fromfile_png_rgb(self):
        # basic smoke test - assume that kiva.image does the right thing
        path = os.path.join(data_dir, 'PngSuite', 'basn2c08.png')
        data_source = ImageData.fromfile(path)

        self.assertEqual(data_source.value_depth, 3)

    def test_fromfile_png_rgba(self):
        # basic smoke test - assume that kiva.image does the right thing
        path = os.path.join(data_dir, 'PngSuite', 'basi6a08.png')
        data_source = ImageData.fromfile(path)

        self.assertEqual(data_source.value_depth, 4)

    def test_metadata(self):
        self.assertEqual(self.data_source.metadata,
                         {'annotations': [], 'selections': []})

    def test_metadata_changed(self):
        with self.assertTraitChanges(self.data_source, 'metadata_changed', count=1):
            self.data_source.metadata = {'new_metadata': True}

    def test_metadata_items_changed(self):
        with self.assertTraitChanges(self.data_source, 'metadata_changed', count=1):
            self.data_source.metadata['new_metadata'] = True
