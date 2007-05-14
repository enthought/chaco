
from cPickle import Pickler, Unpickler, load, dump, loads, dumps
import pdb, unittest

from enthought.traits.api import HasTraits, Str, Float, Enum, Property, Trait, List, \
                             false, true, Instance, Int

# pickling child classes doesn't work well in the unittest framework unless 
# the classes to be pickled are in a different file
from serializable_base import Root, Shape, Circle, Poly

class SimpleSerializationTestCase(unittest.TestCase):
    
    def compare_traits(self, a, b, trait_names=None):
        "Checks the traits of objects 'a' and 'b' and makes sure they all match."
        if trait_names is None:
            trait_names = a.trait_names()
        for name in trait_names:
            if name in ("trait_added", "trait_modified"):
                continue
            o1 = getattr(a,name)
            o2 = getattr(b,name)
            if isinstance(o1, list) or isinstance(o1, tuple):
                print "Warning: Cowardly refusing to do deep compares"
            else:
                self.assert_(o1 == o2)
        return
    
    def create_objects(self):
        "creates some inter-related objects to serialize"
        c1 = Circle(radius=5.0, name="c1", x=1.0, y=2.0)
        c2 = Circle(radius=10.0, name="c2", x=2.0, y=3.0)
        poly = Poly(numside = 12, name="poly")
        self.c1 = c1
        self.c2 = c2
        self.poly = poly
        self.click1 = click1
        return
    
    def test_basic_save(self):
        c = Circle(radius=5.0, name="c1", x=1.0, y=2.0)
        c2 = loads(dumps(c))
        for attrib in ("tools", "filled", "color", "x", "radius"):
            self.assert_(getattr(c, attrib) == getattr(c2, attrib))
        self.failUnlessEqual(c2.y, 2.0)
        return
    
    def test_basic_save2(self):
        p = Poly(numside=3, name="poly", x=3.0, y=4.0)
        p2 = loads(dumps(p))
        for attrib in ("tools", "filled", "color", "x", "numsides", "length"):
            self.assert_(getattr(p, attrib) == getattr(p2, attrib))
        self.failUnlessEqual(p2.y, 4.0)
        return


class PlotSerializationTestCase(unittest.TestCase):
    pass    


def test_suite(level=1):
    suites = []
    suites.append(unittest.makeSuite(SimpleSerializationTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()


# EOF
