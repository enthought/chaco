#------------------------------------------------------------------------------
# Copyright (c) 2014, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------

import unittest

import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal

from chaco.api import DataRange1D
from .. import default_colormaps


class DefaultColormapsTestCase(unittest.TestCase):

    def test_default_colormaps_smoke(self):
        # Runs some data through each of the default colormaps and do basic
        # sanity checks.
        x = np.linspace(-1.5, 2.0, 8)
        datarange = DataRange1D(low_setting=-1.0, high_setting=1.5)
        for cmap_func in default_colormaps.color_map_functions:
            print cmap_func
            cmapper = cmap_func(datarange)
            rgba = cmapper.map_screen(x)
            self.assertEqual(rgba.shape, (8, 4))
            self.assertTrue(np.isfinite(rgba).all())
            self.assertTrue((rgba >= 0.0).all())
            self.assertTrue((rgba <= 1.0).all())
            # No transparency for any of the defaults.
            assert_array_equal(rgba[:, -1], np.ones(8))
            assert_array_equal(rgba[0], rgba[1])
            assert_array_equal(rgba[-2], rgba[-1])
            r_cmapper = default_colormaps.reverse(cmap_func)(datarange)
            r_rgba = r_cmapper.map_screen(x)
            assert_array_almost_equal(r_rgba, rgba[::-1])
            c_cmapper = default_colormaps.center(cmap_func)(datarange)
            self.assertEqual(c_cmapper.range.low, -1.5)
            self.assertEqual(c_cmapper.range.high, 1.5)
            f_cmapper = default_colormaps.fix(cmap_func,
                                              (0.0, 1.0))(datarange)
            self.assertEqual(f_cmapper.range.low, 0.0)
            self.assertEqual(f_cmapper.range.high, 1.0)
