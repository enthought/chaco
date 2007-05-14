""" A putative stylesheet API based on a subset of the CSS2 cascade rules.
"""

# Major library imports
import numpy

# Enthought library imports
from enthought.traits.api import HasTraits, List, Instance

class Selector:
    def match(self, element, ancestors):
        """ Determine if the given element matches this selector.
        """
        raise NotImplementedError


class Rule:
    """
    Matches a selector with a set of styles (defined as a dict)
    """
    def __init__(self, selector, *style, **kw_styles):
        """
        A Rule can be constructed in two ways:
            Rule(selector, styledict)
            Rule(selector, attr1="foo", attr2="bar", ...)
        """
        self.selector = selector
        if len(style) != 0:
            self.style = style[0]
        else:
            self.style = kw_styles
        return

class StyleID(Selector):
    """ Matches by the "style_id" attribute of the element."""
    
    def __init__(self, style_id):
        self.style_id = style_id
        return

    def match(self, element, ancestors):
        if element.style_id != self.style_id:
            return None
        else:
            return numpy.array([1, 0, 0])

class Attribute(Selector):
    """ Matches by any attribute (and, optionally, a value) """

    def __init__(self, attr_name, *value):
        """
        Constructed in one of two ways:
            Attribute(attr_name) - match by name only, ignore value
            Attribute(attr_name, vale) - match by both name and value
        """
        self.attribute = attr_name
        if len(value) != 0:
            self.value = value
            self.check_value = True
        else:
            self.check_value = False
        return

    def match(self, element, ancestors):
        if not hasattr(element, self.attribute):
            return None
        if self.check_value and (getattr(element, self.attribute) != self.value):
            return None
        else:
            return numpy.array([0, 1, 0])

class StyleClass(Selector):
    """ Matches by the "style_class" attribute of the element """
    def __init__(self, style_class):
        self.style_class = style_class
        return

    def match(self, element, ancestors):
        if element.style_class != self.style_class:
            return None
        else:
            return numpy.array([0, 0, 1])

class ClassAndAttribute(Selector):
    """ Matches by style_class and an attribute (and, optionally, a value) """
    def __init__(self, style_class, attr_name, value=None):
        self.style_class = style_class
        self.attr_name = attr_name
        self.value = value
        return
    
    def match(self, element, ancestors):
        if element.style_class != self.style_class:
            return None
        elif (not hasattr(element, self.attr_name) or 
              getattr(element, self.attr_name) != self.value):
            return None
        else:
            return numpy.array([0, 1, 1])

class Descendant(Selector):
    """ Matches by ancestor/descendant relationship. """
    def __init__(self, element, ancestor):
        "element and ancestor are selectors"
        self.element = element
        self.ancestor = ancestor
        return

    def match(self, element, ancestors):
        elem_match = self.element.match(element, ancestors)
        if elem_match is None:
            return None
        anc_match = numpy.zeros(3)
        for i, anc in enumerate(ancestors):
            anc_match = self.ancestor.match(anc, ancestors[i+1:])
            if anc_match is not None:
                break
        if anc_match is not None:
            return anc_match + elem_match
        else:
            return None

class Child(Selector):
    """
    Matches based on a strict parent-child relationship between the parent
    Selector and the child Selector.
    """
    def __init__(self, parent, child):
        self.parent = parent
        self.child = child
        return
    
    def match(self, element, ancestors):
        elem_match = self.child.match(element, ancestors)
        if elem_match is None or not ancestors:
            return None
        parent_match = self.parent.match(ancestors[0], ancestors[1:])
        if parent_match is None:
            return None
        return parent_match + elem_match


class Style(dict):
    """
    A special proxy dictionary that uses attribute access to look up values.
    It also locally stores any values set on it, but searches inside itself
    and another dictionary for lookup. This allows Style objects to have their own
    local style dictionary while looking into a separate cached style.
    
    Deletes also only operate on the local data, and not the proxied dictionary.
    """
    def __init__(self, other_dict=None, **kwds):
        super(Style, self).__init__(kwds)
        self._other_dict = other_dict
        return

    def set_dict(self, otherdict):
        self._other_dict = otherdict
        return

    def __getitem__(self, name):
        try:
            return dict.__getitem__(self, name)
        except KeyError:
            if self._other_dict is not None:
                return self._other_dict[name]
            else:
                raise KeyError, name

    def __str__(self):
        # pretty inefficient but this should only be used for testing anyway
        if self._other_dict:
            tmp = self._other_dict.copy()
            tmp.update(self)
            return tmp.__str__()
        else:
            return dict.__str__(self)

class StyleSheet(HasTraits):
    
    rules = List(Instance(Rule))

    def query(self, element, ancestors):
        matches = []
        for rule in self.rules:
            match = rule.selector.match(element, ancestors)
            if match is not None:
                matches.append((tuple(match), rule.style))
        matches.sort()
        if not matches:
            return Style()
        else:
            return matches[-1][1]


class StyleDB(HasTraits):
    
    user_important_sheet = Instance(StyleSheet)
    app_important_sheet = Instance(StyleSheet)
    app_sheet = Instance(StyleSheet)
    user_sheet = Instance(StyleSheet)
    default_sheet = Instance(StyleSheet)

    def sheets(self):
        if self.user_important_sheet is not None:
            yield self.user_important_sheet
        if self.app_important_sheet is not None:
            yield self.app_important_sheet
        if self.app_sheet is not None:
            yield self.app_sheet
        if self.user_sheet is not None:
            yield self.user_sheet
        if self.default_sheet is not None:
            yield self.default_sheet

    def query(self, element, ancestors):
        for sheet in self.sheets():
            answer = sheet.query(element, ancestors)
            if answer is not None:
                return answer

        # We fell off the end of the style sheet list.
        # Possibly, we should return the empty Style() here.
        return None


__all__ = ['Style', 'Selector', 'Rule', 'StyleID', 'Attribute', 'StyleClass', 
    'ClassAndAttribute', 'Descendant', 'Child', 'Style', 'StyleSheet', 'StyleDB']




