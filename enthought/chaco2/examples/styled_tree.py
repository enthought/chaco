#!/usr/bin/env python
"""
A small example for using the putative stylesheet system.
Not a graphical demo.
"""

# Enthought library imports.
from enthought.traits.api import HasTraits, Instance, Str, List, Any

# Local library imports
from enthought.chaco2.stylesheets import StyleDB, Style, StyleSheet, Rule, \
        Child, Descendant, StyleClass

class Element(HasTraits):

    name = Str

    id = Str

    children = List

    style_class = Str

    style = Instance(Style, args=())

    def walk(self, ancestors=None):
        """ Preorder visitation of each element in the tree below this one.
        """
        if ancestors is None:
            ancestors = []
        yield self, ancestors
        for child in self.children:
            anc = list(ancestors)
            anc.insert(0, self)
            for elem, anc2 in child.walk(anc):
                yield elem, anc2

    def __str__(self):
        return '%s#%s' % (self.name, self.id)

    def add_style(self, style):
        newstyle = Style()
        newstyle.update(style)
        newstyle.update(self.style)
        self.style = newstyle

def decorate_ids(root):
    counter = 0
    for elem, anc in root.walk():
        if elem.id == "":
            elem.id = 'id%.4d' % counter
        counter += 1

def decorate_styles(root, style_db):
    for elem, anc in root.walk():
        if anc:
            parent_style = Style(**anc[0].style)
        else:
            parent_style = Style()
        style = style_db.query(elem, anc)
        if style is not None:
            parent_style.update(style)
        elem.add_style(parent_style)
        print "  " * len(anc) + 'Style for %s: %s' % (elem, elem.style)


tree = Element(style_class='Root', children=[
    Element(style_class='Foo', children=[
        Element(style_class='Bar'),
        Element(style_class='Baz', children=[
            Element(style_class="pwang", id="special")
        ]),
    ]),
    Element(style_class='Bar', children=[
        Element(style_class='Baz', children=[
            Element(style_class="pwang", style=Style()) #font="Helvetica"))
        ]),
    ]),
])

decorate_ids(tree)

style_db = StyleDB(
    default_sheet=StyleSheet(
        rules=[
            Rule(StyleClass('Baz'), Style(color='red')),
            Rule(Child(child=StyleClass('Baz'), parent=StyleClass('Bar')), Style(font='Arial')),
            Rule(StyleClass('Root'), Style(font='Times')),
            Rule(StyleClass("Foo"), Style(hmargin=10)),
            Rule(Descendant(element=StyleClass("pwang"), ancestor=StyleClass("Baz")),
                 Style(color="green")),
            Rule(Descendant(element=Descendant(element=StyleClass("pwang"), ancestor=StyleClass("Baz")),
                            ancestor=StyleClass("Bar")),
                 Style(font="Courier"))
        ],
    ),
)

decorate_styles(tree, style_db)
