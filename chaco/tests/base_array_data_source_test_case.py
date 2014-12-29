"""
Test cases for the BaseArrayDataSource class.
"""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import unittest2 as unittest
import mock
from numpy import arange, array, empty, inf, isfinite, issubdtype, NaN, ones
from numpy.testing import assert_array_equal

from traits.api import ReadOnly, TraitError
from traits.testing.unittest_tools import UnittestTools

from chaco.base import DataInvalidError, DataUpdateError
from chaco.base_array_data_source import BaseArrayDataSource


class TestArrayDataSource(BaseArrayDataSource):
    """ Very simple implementation to test basic functionality """

    #: a 1-D array
    dimension = ReadOnly(1)

    #: with scalar values
    value_type = ReadOnly('scalar')


class TestVectorArrayDataSource(BaseArrayDataSource):
    """ Very simple implementation to test basic functionality """

    #: a 1-D array
    dimension = ReadOnly(1)

    #: with scalar values
    value_type = ReadOnly('vector')


class BaseArrayDataSourceTestCase(unittest.TestCase, UnittestTools):
    """ Test cases for the BaseArrayDataSource class. """

    def setUp(self):
        self.data = arange(12.0)
        self.data[5] = NaN
        self.data_source = TestArrayDataSource(data=self.data)
        self.data_source._empty_data = mock.MagicMock(
            return_value=empty((0,)))

        self.mask = (self.data % 2 == 0)
        self.masked_data_source = TestArrayDataSource(data=self.data,
                                                      mask=self.mask)
        self.masked_data_source._empty_data = mock.MagicMock(
            return_value=empty((0,)))

        self.empty_data_source = TestArrayDataSource()
        self.empty_data_source._empty_data = mock.MagicMock(
            return_value=empty((0,)))

        # something like an array of colors
        self.vector_data = arange(12.0).reshape(4, 3)
        self.vector_data_source = TestVectorArrayDataSource(self.vector_data)
        self.vector_data_source._empty_data = mock.MagicMock(
            return_value=empty((0, 3)))

        # an array of ints
        self.int_data = arange(12)
        self.int_data_source = TestArrayDataSource(data=self.int_data,
                                                   mask=self.mask)
        self.int_data_source._empty_data = mock.MagicMock(
            return_value=empty((0,), dtype=int))

        # an array of strings
        self.text_data = array(['zero', 'one', 'two', 'three', 'four', 'five',
                                'six', 'seven', 'eight', 'nine', 'ten',
                                'eleven'])
        self.text_data_source = TestArrayDataSource(data=self.text_data,
                                                   mask=self.mask)
        self.text_data_source._empty_data = mock.MagicMock(
            return_value=empty((0,), dtype='S1'))


    def test_initialize(self):
        self.validate_data(self.data_source, self.data)
        self.assertEquals(self.data_source.get_bounds(), (0.0, 11.0))

    def test_initialize_masked(self):
        self.validate_data(self.masked_data_source, self.data, self.mask)
        self.assertEquals(self.masked_data_source.get_bounds(), (0.0, 11.0))

    def test_initialize_empty(self):
        data_source = self.empty_data_source
        self.validate_data(data_source, None)

        self.assertEquals(data_source.get_size(), (0,))
        self.assertTrue(data_source._empty_data.called)

        with self.assertRaises(ValueError):
            data_source.get_bounds()

    def test_initialize_vector(self):
        data_source = self.vector_data_source
        self.validate_data(data_source, self.vector_data)
        assert_array_equal(data_source.get_bounds(),
                           array([[0.0, 1.0, 2.0], [9.0, 10.0, 11.0]]))

    def test_initialize_int(self):
        data_source = self.int_data_source
        self.validate_data(data_source, self.int_data, self.mask)
        assert_array_equal(data_source.get_bounds(), (0, 11))

    def test_initialize_text(self):
        data_source = self.text_data_source
        self.validate_data(data_source, self.text_data, self.mask)
        with self.assertRaises(TypeError):
            data_source.get_bounds()

    def test_vector_nan(self):
        data_source = self.vector_data_source
        self.vector_data[2, 2] = NaN
        data_source.set_data(self.vector_data)
        self.validate_data(data_source, self.vector_data)
        assert_array_equal(data_source.get_bounds(),
                           array([[0.0, 1.0, 2.0], [9.0, 10.0, 11.0]]))

    def test_set_data(self):
        data_source = self.data_source
        new_data = arange(15.0)

        with self.assertTraitChanges(data_source, 'data_changed', 1):
            data_source.set_data(new_data)

        self.validate_data(data_source, new_data)
        self.assertEquals(data_source.get_bounds(), (0.0, 14.0))

    def test_set_data_masked(self):
        data_source = self.data_source
        new_data = arange(15.0)
        new_mask = (new_data % 2 == 0)

        with self.assertTraitChanges(data_source, 'data_changed', 1):
            data_source.set_data(new_data, new_mask)

        self.validate_data(data_source, new_data, new_mask)
        self.assertEquals(data_source.get_bounds(), (0.0, 14.0))

    def test_set_data_none(self):
        data_source = self.data_source

        with self.assertTraitChanges(data_source, 'data_changed', 1):
            data_source.set_data(None)

        self.validate_data(data_source, None)

        with self.assertRaises(ValueError):
            self.empty_data_source.get_bounds()

    def test_set_data_all_nan(self):
        data_source = self.data_source
        new_data = empty(shape=(12,))
        new_data[:] = NaN

        with self.assertTraitChanges(data_source, 'data_changed', 1):
            data_source.set_data(new_data)

        self.validate_data(data_source, new_data)

        with self.assertRaises(ValueError):
            self.empty_data_source.get_bounds()

    def test_set_data_invalid(self):
        data_source = self.data_source

        with self.assertRaises(TraitError):
            with self.assertTraitDoesNotChange(data_source, 'data_changed'):
                data_source.set_data('invalid data')

        self.check_invalid(data_source)

        # now check that we can reset to valid state
        with self.assertTraitChanges(data_source, 'data_changed', 1):
            data_source.set_data(self.data)

        self.validate_data(data_source, self.data)

    def test_set_data_update_lock_fail(self):
        data_source = self.data_source
        new_data = arange(15.0)

        with self.assertTraitDoesNotChange(data_source, 'data_changed'):
            with self.assertRaises(DataUpdateError):
                with data_source._update_lock:
                    data_source.set_data(new_data)

        # data should be unmodified by failed update
        self.validate_data(data_source, self.data)

    def test_masked_data_set_data(self):
        data_source = self.data_source
        new_data = arange(0, 24.0, 2)

        with self.assertTraitChanges(data_source, 'data_changed', 1):
            data_source.set_data(new_data)

        self.validate_data(data_source, new_data)
        self.assertEquals(data_source.get_bounds(), (0.0, 22.0))

    def test_set_mask(self):
        data_source = self.data_source
        new_mask = (self.data % 3 == 0)

        with self.assertTraitChanges(data_source, 'data_changed', 1):
            data_source.set_mask(new_mask)

        self.validate_data(data_source, self.data, new_mask)
        self.assertEquals(data_source.get_bounds(), (0.0, 11.0))

    def test_set_mask_update_lock_fail(self):
        data_source = self.data_source
        new_mask = (self.data % 3 == 0)

        with self.assertTraitDoesNotChange(data_source, 'data_changed'):
            with self.assertRaises(DataUpdateError):
                with data_source._update_lock:
                    data_source.set_mask(new_mask)

    def test_remove_mask(self):
        data_source = self.masked_data_source

        with self.assertTraitChanges(data_source, 'data_changed', 1):
            data_source.remove_mask()

        self.validate_data(data_source, self.data)
        self.assertEquals(data_source.get_bounds(), (0.0, 11.0))

    def test_invalidate_data(self):
        data_source = self.data_source

        with self.assertTraitDoesNotChange(data_source, 'data_changed'):
            data_source.invalidate_data()

        self.check_invalid(data_source)

        # now check that we can reset to valid state
        with self.assertTraitChanges(data_source, 'data_changed', 1):
            data_source.set_data(self.data)

        self.validate_data(data_source, self.data)

    def test_access_guard(self):
        data_source = self.data_source

        with self.assertRaises(DataInvalidError):
            with data_source.access_guard():
                data_source.invalidate_data()

        self.check_invalid(data_source)

        # now check that we can reset to valid state
        with self.assertTraitChanges(data_source, 'data_changed', 1):
            data_source.set_data(self.data)

        self.validate_data(data_source, self.data)

    def test_data_mask_incompatible(self):
        data_source = TestArrayDataSource(self.data, (arange(15.0) % 3 == 0))

        with self.assertRaises(ValueError):
            data_source.get_data_mask()

    def test_get_bounds_plus_infinity(self):
        self.data[3] = inf
        data_source = TestArrayDataSource(self.data)

        self.assertEquals(data_source.get_bounds(), (0, inf))

    def test_get_bounds_all_plus_infinity(self):
        self.data[:] = inf
        data_source = TestArrayDataSource(self.data)

        self.assertEquals(data_source.get_bounds(), (inf, inf))

    def test_get_bounds_minus_infinity(self):
        self.data[3] = -inf
        data_source = TestArrayDataSource(self.data)

        self.assertEquals(data_source.get_bounds(), (-inf, 11))

    def test_get_bounds_all_minus_infinity(self):
        self.data[:] = -inf
        data_source = TestArrayDataSource(self.data)

        self.assertEquals(data_source.get_bounds(), (-inf, -inf))

    def test_get_bounds_plus_minus_infinity(self):
        self.data[3] = inf
        self.data[7] = -inf
        data_source = TestArrayDataSource(self.data)

        self.assertEquals(data_source.get_bounds(), (-inf, inf))

    def test_get_bounds_vector_plus_infinity(self):
        data_source = self.vector_data_source
        self.vector_data[2, 2] = inf
        data_source.set_data(self.vector_data)
        self.validate_data(data_source, self.vector_data)
        assert_array_equal(data_source.get_bounds()[0],
                           array([0.0, 1.0, 2.0]))
        assert_array_equal(data_source.get_bounds()[1],
                           array([9.0, 10.0, inf]))

    def test_get_bounds_vector_minus_infinity(self):
        data_source = self.vector_data_source
        self.vector_data[2, 2] = -inf
        data_source.set_data(self.vector_data)
        self.validate_data(data_source, self.vector_data)
        assert_array_equal(data_source.get_bounds()[0],
                           array([0.0, 1.0, -inf]))
        assert_array_equal(data_source.get_bounds()[1],
                           array([9.0, 10.0, 11.0]))

    def test_get_bounds_vector_plus_minus_infinity(self):
        data_source = self.vector_data_source
        self.vector_data[2, 2] = -inf
        self.vector_data[2, 1] = inf
        data_source.set_data(self.vector_data)
        self.validate_data(data_source, self.vector_data)
        assert_array_equal(data_source.get_bounds()[0],
                           array([0.0, 1.0, -inf]))
        assert_array_equal(data_source.get_bounds()[1],
                           array([9.0, inf, 11.0]))

    def test_get_bounds_vector_nan_vector(self):
        data_source = self.vector_data_source
        self.vector_data[:, 2] = NaN
        data_source.set_data(self.vector_data)

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

    def test_empty_data_not_implemented(self):
        data_source = BaseArrayDataSource()

        with self.assertRaises(NotImplementedError):
            data_source.get_data()

    #### Common validation methods ###########################################

    def validate_data(self, data_source, expected_data, expected_mask=None):
        if expected_data is None:
            expected_empty = True
        else:
            expected_empty = False
            expected_shape = expected_data.shape[:data_source.dimension]

        if expected_mask is None:
            if not expected_empty:
                axes = tuple(range(1, len(expected_data.shape)))
                try:
                    expected_mask = isfinite(expected_data).all(axis=axes)
                except TypeError:
                    expected_mask = ones(expected_data.shape, dtype=bool)
                expected_is_masked = not expected_mask.all()
            else:
                expected_is_masked = False
        else:
            if not expected_empty:
                axes = tuple(range(1, len(expected_data.shape)))
                try:
                    expected_mask &= isfinite(expected_data).all(axis=axes)
                except TypeError:
                    pass
            expected_is_masked = True

        # check that get_data() works
        data = data_source.get_data()

        self.assertEqual(data_source._empty_data.called, expected_empty)
        if not expected_empty:
            assert_array_equal(data, expected_data)

        # check that get_data_mask() works
        data, mask = data_source.get_data_mask()

        self.assertEqual(data_source._empty_data.called, expected_empty)
        if not expected_empty:
            assert_array_equal(data, expected_data)
            assert_array_equal(mask, expected_mask)

        # check that is_masked() works
        self.assertEqual(data_source.is_masked(), expected_is_masked)

        # check that get_size() works
        if not expected_empty:
            self.assertEquals(data_source.get_size(), expected_shape)

    def check_invalid(self, data_source):
        # check that methods to get data fail
        with self.assertRaises(DataInvalidError):
            data_source.get_data()

        with self.assertRaises(DataInvalidError):
            data_source.get_data_mask()

        with self.assertRaises(DataInvalidError):
            data_source.is_masked()

        with self.assertRaises(DataInvalidError):
            data_source.get_size()

        with self.assertRaises(DataInvalidError):
            data_source.get_bounds()
