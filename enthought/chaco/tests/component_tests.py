from enable.api import Component


def test_padding_init():
    """ Make sure that padding traits passed to the constructor get set in the
    correct order.
    """
    c = Component()
    assert c.padding_top == 0
    assert c.padding_bottom == 0
    assert c.padding_left == 0
    assert c.padding_right == 0
    c = Component(padding=50)
    assert c.padding_top == 50
    assert c.padding_bottom == 50
    assert c.padding_left == 50
    assert c.padding_right == 50
    c = Component(padding=50, padding_top=15)
    assert c.padding_top == 15
    assert c.padding_bottom == 50
    assert c.padding_left == 50
    assert c.padding_right == 50
    c = Component(padding=50, padding_bottom=15)
    assert c.padding_top == 50
    assert c.padding_bottom == 15
    assert c.padding_left == 50
    assert c.padding_right == 50
    c = Component(padding=50, padding_left=15)
    assert c.padding_top == 50
    assert c.padding_bottom == 50
    assert c.padding_left == 15
    assert c.padding_right == 50
    c = Component(padding=50, padding_right=15)
    assert c.padding_top == 50
    assert c.padding_bottom == 50
    assert c.padding_left == 50
    assert c.padding_right == 15

def test_padding_trait_default():
    class PaddedComponent(Component):
        padding_top = 50
    c = PaddedComponent()
    assert c.padding_top == 50
    assert c.padding_bottom == 0
    assert c.padding_left == 0
    assert c.padding_right == 0
    c = PaddedComponent(padding_left=15)
    assert c.padding_top == 50
    assert c.padding_bottom == 0
    assert c.padding_left == 15
    assert c.padding_right == 0

