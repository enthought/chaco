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

from traits.api import Float, HasTraits, Int, Map, Str
from enable.api import ColorTrait

from ..chaco_traits import MappedUnion, Optional


class UsesMappedUnion(HasTraits):

    no_mapped = MappedUnion(Int, Float)

    mapped = MappedUnion(
        None, Str, Map({'yes': True, 'no': False}), ColorTrait
    )

    optional = Optional(ColorTrait)

    optional_default = Optional(ColorTrait, default_value='red')


class TestMappedUnion(unittest.TestCase):

    def test_no_mapped(self):
        no_mapped = MappedUnion(Int, Float)

        self.assertFalse(no_mapped.is_mapped)
        self.assertIsNone(no_mapped.post_setattr)

    def test_mapped(self):
        mapped = MappedUnion(None, Str, Map({'yes': True, 'no': False}))

        self.assertTrue(mapped.is_mapped)
        self.assertIsNotNone(mapped.post_setattr)

    def test_optional(self):
        mapped = Optional(ColorTrait)

        self.assertTrue(mapped.is_mapped)
        self.assertIsNotNone(mapped.post_setattr)

    def test_no_mapped_class(self):
        mapped_union = UsesMappedUnion()

        no_mapped = mapped_union.trait('no_mapped')

        self.assertFalse(no_mapped.is_mapped)
        self.assertIsNone(no_mapped.post_setattr)

        self.assertFalse(hasattr(mapped_union, 'no_mapped_'))

        mapped_union.no_mapped = 1

        self.assertFalse(hasattr(mapped_union, 'no_mapped_'))

    def test_mapped_class(self):
        mapped_union = UsesMappedUnion()

        mapped = mapped_union.trait('mapped')

        self.assertTrue(mapped.is_mapped)
        self.assertIsNotNone(mapped.post_setattr)

        # test default
        self.assertIsNone(mapped_union.mapped_)

        # test mapper works
        mapped_union.mapped = 'yes'

        self.assertTrue(mapped_union.mapped_)

        # test second mapper works
        mapped_union.mapped = 'red'

        self.assertEqual(mapped_union.mapped_, (1.0, 0.0, 0.0, 1.0))

        # test non-mapped value works
        mapped_union.mapped = 'notacolor'

        self.assertEqual(mapped_union.mapped_, 'notacolor')

    def test_optional_class(self):
        mapped_union = UsesMappedUnion()

        optional = mapped_union.trait('optional')

        self.assertTrue(optional.is_mapped)
        self.assertIsNotNone(optional.post_setattr)

        # test default
        self.assertIsNone(mapped_union.optional_)

        # test mapper works
        mapped_union.optional = 'red'

        self.assertEqual(mapped_union.optional_, (1.0, 0.0, 0.0, 1.0))

        # test non-mapped value works
        mapped_union.optional = None

        self.assertIsNone(mapped_union.optional_)

    def test_optional_default_class(self):
        mapped_union = UsesMappedUnion()

        # test default
        self.assertEqual(mapped_union.optional_default_, (1.0, 0.0, 0.0, 1.0))
