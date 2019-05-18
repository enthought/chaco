import unittest

from enable.api import Component


class TestComponent(unittest.TestCase):
    # FIXME: It is debatable whether this should remain part of Chaco,
    # or be moved to Enable.
    
    def test_padding_init(self):
        """ Make sure that padding traits passed to the constructor get set in the
        correct order.
        """
        c = Component()
        self.assertEqual(c.padding_top, 0)
        self.assertEqual(c.padding_bottom, 0)
        self.assertEqual(c.padding_left, 0)
        self.assertEqual(c.padding_right, 0)
        c = Component(padding=50)
        self.assertEqual(c.padding_top, 50)
        self.assertEqual(c.padding_bottom, 50)
        self.assertEqual(c.padding_left, 50)
        self.assertEqual(c.padding_right, 50)
        c = Component(padding=50, padding_top=15)
        self.assertEqual(c.padding_top, 15)
        self.assertEqual(c.padding_bottom, 50)
        self.assertEqual(c.padding_left, 50)
        self.assertEqual(c.padding_right, 50)
        c = Component(padding=50, padding_bottom=15)
        self.assertEqual(c.padding_top, 50)
        self.assertEqual(c.padding_bottom, 15)
        self.assertEqual(c.padding_left, 50)
        self.assertEqual(c.padding_right, 50)
        c = Component(padding=50, padding_left=15)
        self.assertEqual(c.padding_top, 50)
        self.assertEqual(c.padding_bottom, 50)
        self.assertEqual(c.padding_left, 15)
        self.assertEqual(c.padding_right, 50)
        c = Component(padding=50, padding_right=15)
        self.assertEqual(c.padding_top, 50)
        self.assertEqual(c.padding_bottom, 50)
        self.assertEqual(c.padding_left, 50)
        self.assertEqual(c.padding_right, 15)

    def test_padding_trait_default(self):
        class PaddedComponent(Component):
            padding_top = 50
        c = PaddedComponent()
        self.assertEqual(c.padding_top, 50)
        self.assertEqual(c.padding_bottom, 0)
        self.assertEqual(c.padding_left, 0)
        self.assertEqual(c.padding_right, 0)
        c = PaddedComponent(padding_left=15)
        self.assertEqual(c.padding_top, 50)
        self.assertEqual(c.padding_bottom, 0)
        self.assertEqual(c.padding_left, 15)
        self.assertEqual(c.padding_right, 0)
