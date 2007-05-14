
import unittest
import pdb

from enthought.chaco2.api import Stylable, Style, StyleSheet
from enthought.chaco2.stylesheets import *  # the selectors, etc.
from enthought.traits.api import HasTraits, List, Str, This, Trait

class MyThing(Stylable):
    name = Str
    parent = Trait(None, None, This)
    children = List
    
    # Redefine style class for testing purposes to not be a class attribute, but
    # rather an instance trait
    style_class = Str("")

    _indent = "    "

    def __init__(self, name="", parent=None, styleclass=""):
        self.name = name
        self.style_id = name
        self.parent = parent
        if styleclass == "":
            self.style_class = name
        return
    
    def _parent_changed(self, old, new):
        if old is not None:
            old.remove(self)
        if new is not None:
            new.add(self)
        self.style_parent = new
        return

    def add(self, child):
        if child not in self.children:
            self.children.append(child)
        return

    def remove(self, child):
        if child in self.children:
            self.children.remove(child)
        return

    def dump(self, indentlevel=0):
        s = indentlevel * self._indent + self.name + ":"
        print s, self.style, "    (", self.style._other_dict, ")"
        #print " " * len(s) + "parent style:", self.parent._c
        for child in self.children:
            child.dump(indentlevel+1)
        return


def create_ss():
    s = StyleSheet(rules = [
            Rule(StyleClass("a"), Style(color="red", weight=5.0)),
            Rule(StyleID("c"), Style(happiness=-2.0, weight=3.0)),
            Rule(Attribute("bogus"), Style(color="green")),
            Rule(Attribute("bogus", "Some bogus blue attribute"), Style(color="blue")),
            Rule(StyleClass("b"), Style(weight=7.0))
        ])
    return s

if __name__ == "__main__":
    # Create the tree
    root = MyThing("root")
    a = MyThing("a", root)
    b = MyThing("b", a)
    b.bogus = "Some bogus green attribute"
    c = MyThing("c", a)
    cc = MyThing("cc", c)
    ccc = MyThing("ccc", c)
    ccc.bogus = "Some bogus blue attribute"
    d = MyThing("d", root)
    e = MyThing("e", d)

    s = create_ss()
    print "**************** Setting stylesheet ****************"
    root.stylesheet = s
    
    root.dump()



