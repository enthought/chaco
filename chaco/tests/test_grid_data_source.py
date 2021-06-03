# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests of GridDataSource behavior.
"""

import unittest

from numpy import array
from numpy.testing import assert_array_equal

from chaco.api import GridDataSource
from traits.testing.api import UnittestTools


class GridDataSourceTestCase(UnittestTools, unittest.TestCase):
    def setUp(self):
        self.data_source = GridDataSource(
            xdata=array([1, 2, 3]),
            ydata=array([1.5, 0.5, -0.5, -1.5]),
            sort_order=("ascending", "descending"),
        )

    def test_empty(self):
        data_source = GridDataSource()
        self.assertEqual(data_source.sort_order, ("none", "none"))
        self.assertEqual(data_source.index_dimension, "image")
        self.assertEqual(data_source.value_dimension, "scalar")
        self.assertEqual(
            data_source.metadata, {"selections": [], "annotations": []}
        )
        xdata, ydata = data_source.get_data()
        assert_array_equal(xdata.get_data(), array([]))
        assert_array_equal(ydata.get_data(), array([]))
        self.assertEqual(data_source.get_bounds(), ((0, 0), (0, 0)))

    def test_init(self):
        test_xd = array([1, 2, 3])
        test_yd = array([1.5, 0.5, -0.5, -1.5])
        test_sort_order = ("ascending", "descending")

        self.assertEqual(self.data_source.sort_order, test_sort_order)
        xd, yd = self.data_source.get_data()
        assert_array_equal(xd.get_data(), test_xd)
        assert_array_equal(yd.get_data(), test_yd)
        self.assertEqual(
            self.data_source.get_bounds(),
            ((min(test_xd), min(test_yd)), (max(test_xd), max(test_yd))),
        )

    def test_set_data(self):

        test_xd = array([0, 2, 4])
        test_yd = array([0, 1, 2, 3, 4, 5])
        test_sort_order = ("none", "none")

        self.data_source.set_data(
            xdata=test_xd, ydata=test_yd, sort_order=("none", "none")
        )

        self.assertEqual(self.data_source.sort_order, test_sort_order)
        xd, yd = self.data_source.get_data()
        assert_array_equal(xd.get_data(), test_xd)
        assert_array_equal(yd.get_data(), test_yd)
        self.assertEqual(
            self.data_source.get_bounds(),
            ((min(test_xd), min(test_yd)), (max(test_xd), max(test_yd))),
        )

    def test_metadata(self):
        self.assertEqual(
            self.data_source.metadata, {"annotations": [], "selections": []}
        )

    def test_metadata_changed(self):
        with self.assertTraitChanges(
            self.data_source, "metadata_changed", count=1
        ):
            self.data_source.metadata = {"new_metadata": True}

    def test_metadata_items_changed(self):
        with self.assertTraitChanges(
            self.data_source, "metadata_changed", count=1
        ):
            self.data_source.metadata["new_metadata"] = True
