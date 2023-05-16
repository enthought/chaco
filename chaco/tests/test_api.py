# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

import chaco.api


class TestAPI(unittest.TestCase):

    def test_enable_imports(self):
        """Test for deprecated imports from enable.api"""
        names = {'marker_trait'}
        for name in names:
            with self.subTest(name=name):
                with self.assertWarns(DeprecationWarning):
                    getattr(chaco.api, name)
