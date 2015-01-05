"""
Test cases for the BaseDataSource class.
"""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import unittest2 as unittest
import mock
from numpy import arange, array, empty, inf, isfinite, NaN, ones, prod
from numpy.testing import assert_array_equal

from traits.api import Array, ReadOnly, TraitError
from traits.testing.unittest_tools import UnittestTools

from chaco.base import DataInvalidError, DataUpdateError, DataBoundsError
from chaco.base_data_source import BaseDataSource


class TestArrayDataSource(BaseDataSource):
    """ Very simple implementation to test basic functionality """

    #: a 1-D array
    dimension = ReadOnly(1)

    #: with scalar values
    value_type = ReadOnly('scalar')

    def __init__(self, **traits):
        super(TestArrayDataSource, self).__init__(**traits)
        self._data_valid = True


class BaseDataSourceTestCase(unittest.TestCase, UnittestTools):
    """ Test cases for the BaseArrayDataSource class. """

    def setUp(self):
        self.data = arange(12.0)
        self.data[5] = NaN
        self.data_source = TestArrayDataSource()
        self.data_source._get_data_unsafe = mock.MagicMock(
            return_value=self.data)

        self.empty_data = empty(shape=(0,), dtype=float)
        self.empty_data_source = TestArrayDataSource()
        self.empty_data_source._get_data_unsafe = mock.MagicMock(
            return_value=self.empty_data)

        # something like an array of colors
        self.vector_data = arange(12.0).reshape(4, 3)
        self.vector_data_source = TestArrayDataSource()
        self.vector_data_source._get_data_unsafe = mock.MagicMock(
            return_value=self.vector_data)

        # an array of ints
        self.int_data = arange(12)
        self.int_data_source = TestArrayDataSource()
        self.int_data_source._get_data_unsafe = mock.MagicMock(
            return_value=self.int_data)

        # an array of strings
        self.text_data = array(['zero', 'one', 'two', 'three', 'four', 'five',
                                'six', 'seven', 'eight', 'nine', 'ten',
                                'eleven'])
        self.text_data_source = TestArrayDataSource()
        self.text_data_source._get_data_unsafe = mock.MagicMock(
            return_value=self.text_data)

    def test_data(self):
        self.validate_data(self.data_source, self.data)
        self.data_source._get_data_unsafe.reset_mock()

        self.data_source._get_data_unsafe.reset_mock()
        self.assertEquals(self.data_source.get_bounds(), (0.0, 11.0))
        self.assertTrue(self.data_source._get_data_unsafe.called)

        # and check caching of result of get_bounds
        self.data_source._get_data_unsafe.reset_mock()
        self.assertEquals(self.data_source.get_bounds(), (0.0, 11.0))
        self.assertFalse(self.data_source._get_data_unsafe.called)

    def test_empty_data(self):
        data_source = self.empty_data_source
        self.validate_data(data_source, self.empty_data)
        with self.assertRaises(DataBoundsError):
            data_source.get_bounds()

    def test_vector_data(self):
        data_source = self.vector_data_source
        self.validate_data(data_source, self.vector_data)
        assert_array_equal(data_source.get_bounds(),
                           array([[0.0, 1.0, 2.0], [9.0, 10.0, 11.0]]))

    def test_int_data(self):
        data_source = self.int_data_source
        self.validate_data(data_source, self.int_data)
        assert_array_equal(data_source.get_bounds(), (0, 11))

    def test_text_data(self):
        data_source = self.text_data_source
        self.validate_data(data_source, self.text_data)
        with self.assertRaises(TypeError):
            data_source.get_bounds()

    def test_vector_nan(self):
        data_source = self.vector_data_source
        self.vector_data[2, 2] = NaN
        data_source.data = self.vector_data

        self.validate_data(data_source, self.vector_data)
        assert_array_equal(data_source.get_bounds(),
                           array([[0.0, 1.0, 2.0], [9.0, 10.0, 11.0]]))


    def test_updating_data_update_lock_fail(self):
        data_source = self.data_source

        with self.assertTraitDoesNotChange(data_source, 'data_changed'):
            with self.assertRaises(DataUpdateError):
                with data_source._update_lock:
                    with self.data_source.updating_data():
                        pass

        # data should be unmodified by failed update, and still valid
        self.validate_data(data_source, self.data)

    def test_invalidate_data(self):
        data_source = self.data_source
        # validate everything to ensure that caches are filled
        self.validate_data(data_source, self.data)
        self.assertEquals(self.data_source.get_bounds(), (0.0, 11.0))

        with self.assertTraitDoesNotChange(data_source, 'data_changed'):
            data_source.invalidate_data()

        self.check_invalid(data_source)

        # now check that we can reset to valid state
        self.data_source._get_data_unsafe.reset_mock()

        with self.assertTraitChanges(data_source, 'data_changed', 1):
            with data_source.updating_data():
                pass

        # if caches are filled, is_masked() test should fail
        self.validate_data(data_source, self.data)

        # if caches are filled, this should fail
        self.data_source._get_data_unsafe.reset_mock()
        self.assertEquals(self.data_source.get_bounds(), (0.0, 11.0))
        self.assertTrue(self.data_source._get_data_unsafe.called)

    def test_access_guard(self):
        data_source = self.data_source
        # validate everything to ensure that caches are filled
        self.validate_data(data_source, self.data)
        self.assertEquals(self.data_source.get_bounds(), (0.0, 11.0))

        with self.assertRaises(DataInvalidError):
            with data_source.access_guard():
                data_source.invalidate_data()

        self.check_invalid(data_source)

        # now check that we can reset to valid state
        self.data_source._get_data_unsafe.reset_mock()

        with self.assertTraitChanges(data_source, 'data_changed', 1):
            with data_source.updating_data():
                pass

        # if caches are filled, is_masked() test should fail
        self.validate_data(data_source, self.data)

        # if caches are filled, this should fail
        self.data_source._get_data_unsafe.reset_mock()
        self.assertEquals(self.data_source.get_bounds(), (0.0, 11.0))
        self.assertTrue(self.data_source._get_data_unsafe.called)

    def test_get_bounds_all_nan(self):
        data_source = self.data_source
        self.data[:] = NaN

        self.validate_data(data_source, self.data)

        with self.assertRaises(DataBoundsError):
            self.empty_data_source.get_bounds()

    def test_get_bounds_plus_infinity(self):
        self.data[3] = inf
        data_source = self.data_source

        self.assertEquals(data_source.get_bounds(), (0, inf))

    def test_get_bounds_all_plus_infinity(self):
        self.data[:] = inf
        data_source = self.data_source

        self.assertEquals(data_source.get_bounds(), (inf, inf))

    def test_get_bounds_minus_infinity(self):
        self.data[3] = -inf
        data_source = self.data_source

        self.assertEquals(data_source.get_bounds(), (-inf, 11))

    def test_get_bounds_all_minus_infinity(self):
        self.data[:] = -inf
        data_source = self.data_source

        self.assertEquals(data_source.get_bounds(), (-inf, -inf))

    def test_get_bounds_plus_minus_infinity(self):
        self.data[3] = inf
        self.data[7] = -inf
        data_source = self.data_source

        self.assertEquals(data_source.get_bounds(), (-inf, inf))

    def test_get_bounds_vector_plus_infinity(self):
        data_source = self.vector_data_source
        self.vector_data[2, 2] = inf
        data_source.data = self.vector_data

        self.validate_data(data_source, self.vector_data)
        assert_array_equal(data_source.get_bounds()[0],
                           array([0.0, 1.0, 2.0]))
        assert_array_equal(data_source.get_bounds()[1],
                           array([9.0, 10.0, inf]))

    def test_get_bounds_vector_minus_infinity(self):
        data_source = self.vector_data_source
        self.vector_data[2, 2] = -inf
        data_source.data = self.vector_data

        self.validate_data(data_source, self.vector_data)
        assert_array_equal(data_source.get_bounds()[0],
                           array([0.0, 1.0, -inf]))
        assert_array_equal(data_source.get_bounds()[1],
                           array([9.0, 10.0, 11.0]))

    def test_get_bounds_vector_plus_minus_infinity(self):
        data_source = self.vector_data_source
        self.vector_data[2, 2] = -inf
        self.vector_data[2, 1] = inf
        data_source.data = self.vector_data

        self.validate_data(data_source, self.vector_data)
        assert_array_equal(data_source.get_bounds()[0],
                           array([0.0, 1.0, -inf]))
        assert_array_equal(data_source.get_bounds()[1],
                           array([9.0, inf, 11.0]))

    def test_get_bounds_vector_nan_vector(self):
        data_source = self.vector_data_source
        self.vector_data[:, 2] = NaN
        data_source.data = self.vector_data

        self.validate_data(data_source, self.vector_data)
        with self.assertRaises(ValueError):
            data_source.get_bounds()

    def test_metadata_changed(self):
        with self.assertTraitChanges(self.data_source, 'metadata_changed',
                                     count=1):
            self.data_source.metadata = {'new_metadata': True}

    def test_metadata_items_changed(self):
        with self.assertTraitChanges(self.data_source, 'metadata_changed',
                                     count=1):
            self.data_source.metadata['new_metadata'] = True

    def test_get_data_not_implemented(self):
        data_source = BaseDataSource()

        self.check_invalid(data_source)

    def test_get_data_not_implemented_valid_data(self):
        data_source = BaseDataSource(_data_valid=True)

        with self.assertRaises(NotImplementedError):
            data_source.get_data()

        with self.assertRaises(NotImplementedError):
            data_source.get_data_mask()

        with self.assertRaises(NotImplementedError):
            data_source.is_masked()

        with self.assertRaises(NotImplementedError):
            data_source.get_shape()

        with self.assertRaises(NotImplementedError):
            data_source.get_size()

        with self.assertRaises(NotImplementedError):
            data_source.get_bounds()

    #### Common validation methods ###########################################

    def validate_data(self, data_source, expected_data):
        expected_shape = expected_data.shape[:data_source.dimension]

        axes = tuple(range(1, len(expected_data.shape)))
        try:
            expected_mask = isfinite(expected_data).all(axis=axes)
        except TypeError:
            expected_mask = ones(expected_data.shape, dtype=bool)
        expected_is_masked = not expected_mask.all()

        # check that get_data() works
        data = data_source.get_data()

        self.assertTrue(data_source._get_data_unsafe.called)
        assert_array_equal(data, expected_data)

        # check that is_masked() works
        data_source._get_data_unsafe.reset_mock()
        self.assertEqual(data_source.is_masked(), expected_is_masked)
        self.assertTrue(data_source._get_data_unsafe.called)

        # check that get_data_mask() works
        data_source._get_data_unsafe.reset_mock()
        data, mask = data_source.get_data_mask()

        assert_array_equal(data, expected_data)
        assert_array_equal(mask, expected_mask)
        self.assertTrue(data_source._get_data_unsafe.called)

        # check that get_shape() works
        data_source._get_data_unsafe.reset_mock()
        self.assertEquals(data_source.get_size(), expected_shape)
        self.assertTrue(data_source._get_data_unsafe.called)

        # check that get_size() works
        data_source._get_data_unsafe.reset_mock()
        self.assertEquals(data_source.get_size(), prod(expected_shape))
        self.assertTrue(data_source._get_data_unsafe.called)

    def check_invalid(self, data_source):
        # check that methods to get data fail
        with self.assertRaises(DataInvalidError):
            data_source.get_data()

        with self.assertRaises(DataInvalidError):
            data_source.get_data_mask()

        with self.assertRaises(DataInvalidError):
            data_source.is_masked()

        with self.assertRaises(DataInvalidError):
            data_source.get_shape()

        with self.assertRaises(DataInvalidError):
            data_source.get_size()

        with self.assertRaises(DataInvalidError):
            data_source.get_bounds()
