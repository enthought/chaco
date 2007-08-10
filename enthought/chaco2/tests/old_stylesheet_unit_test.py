

import unittest

from enthought.chaco2.stylable import StyleDict

def create_tree_from_string(s):
    "Returns a tree from a textual representation"
    pass

class StyleDictTestCase(unittest.TestCase):
    def test_simple_lookup(self):
        other_dict = { "a": "A", "b": "B" }
        #pdb.set_trace()
        style = StyleDict(other_dict, foo="FOO", bar="BAR")
        self.assert_( style["foo"] == "FOO" )
        self.assert_( style.foo == "FOO" )
        self.assert_( style["a"] == "A" )
        self.assert_( style.b == "B" )
        self.assert_( "a" in style )
        self.assert_( "foo" in style )
        self.assert_( "bar" not in other_dict )
        return
        
    def test_setting(self):
        other_dict = { "a": "A", "b": "B" }
        style = StyleDict(other_dict, foo="FOO", bar="BAR")
        style.boo = "BOO"
        style["bazzle"] = "BAZZLE"
        self.assert_( style["a"] == "A" )
        self.assert_( style["boo"] == "BOO" )
        self.assert_( style.boo == "BOO" )
        self.assert_( style.bazzle == "BAZZLE" )
        self.assert_( "bazzle" in style )
        self.assert_( "bazzle" not in other_dict )
        self.assert_( "boo" in style )
        self.assert_( "boo" not in other_dict )
        return


class StylableTestCase(unittest.TestCase):
    
    pass


def test_suite(level=1):
    suites = []
    suites.append(unittest.makeSuite(StyleDictTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()
