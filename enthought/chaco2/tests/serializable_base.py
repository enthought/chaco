
from cPickle import Pickler, Unpickler, load, dump, loads, dumps
import pdb, unittest

from enthought.traits.api import HasTraits, Str, Float, Enum, Property, Trait, List, \
                             false, true, Instance, Int
from enthought.chaco2.serializable import Serializable

class Root(HasTraits):
    name = Str
    x = Float(0.0)
    y = Float(0.0)

class Shape(Serializable, Root):
    color = Enum("red", "green", "blue")
    filled = true
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
