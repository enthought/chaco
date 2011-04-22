

from traits.api import Bool, HasTraits, Str, Float, Enum, List, Int
from chaco.serializable import Serializable

class Root(HasTraits):
    name = Str
    x = Float(0.0)
    y = Float(0.0)

class Shape(Serializable, Root):
    color = Enum("red", "green", "blue")
    filled = Bool(True)
    tools = List
    _pickles = ("tools", "filled", "color", "x")

class Circle(Shape):
    radius = Float(10.0)
    _pickles = ("radius",)

class Poly(Shape):
    numsides = Int(5)
    length = Float(5.0)
    _pickles = ("numsides", "length")

# EOF
