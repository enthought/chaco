""" Defines the TraitsTool and Fifo classes, and get_nested_components90
function.
"""
# Enthought library imports
from enable.api import BaseTool, Container
from traits.api import List, Dict, Str

# Chaco imports
from chaco.axis import PlotAxis
from chaco.color_bar import ColorBar


class Fifo(object):
    """Slightly-modified version of the Fifo class from the Python cookbook:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/68436
    """

    def __init__(self):
        self.nextin = 0
        self.nextout = 0
        self.data = {}

    def append(self, value):
        self.data[self.nextin] = value
        self.nextin += 1

    def extend(self, values):
        if len(values) > 0:
            for i, val in enumerate(values):
                self.data[i + self.nextin] = val
            self.nextin += i + 1

    def isempty(self):
        return self.nextout >= self.nextin

    def pop(self):
        value = self.data[self.nextout]
        del self.data[self.nextout]
        self.nextout += 1
        return value


def get_nested_components(container, classes):
    """Returns a list of fundamental plotting components from a container
    with nested containers.

    Performs a breadth-first search of the containment hierarchy. Each element
    in the returned list is a tuple (component, (x,y)) where (x,y) is the
    coordinate frame offset of the component from the top-level container.
    """
    components = []
    worklist = Fifo()
    worklist.append((container, (0, 0)))
    while 1:
        item, offset = worklist.pop()
        if isinstance(item, Container):
            new_offset = (offset[0] + item.x, offset[1] + item.y)
            for c in item.components:
                worklist.append((c, new_offset))
            for overlay in item.overlays + item.underlays:
                components.append((overlay, offset))
        elif any([isinstance(item, klass) for klass in classes]):
            components.append((item, offset))
            for overlay in item.overlays + item.underlays:
                components.append((overlay, offset))
        if worklist.isempty():
            break
    return components


class TraitsTool(BaseTool):
    """Tool to edit the traits of plots, grids, and axes."""

    #: This tool does not have a visual representation (overrides BaseTool).
    draw_mode = "none"
    #: This tool is not visible (overrides BaseTool).
    visible = False

    #: The classes of components that should trigger a traits view
    classes = List([PlotAxis, ColorBar])

    #: A dict of Class : View providing alternate views for a particular component
    views = Dict

    #: The event to trigger the edit on
    event = Str("left_dclick")

    def _dispatch_stateful_event(self, event, suffix):
        """If the event type matches the specification in *event*, look for a component that
        matches one of the classes in *classes* in our containment hierarchy.  If one is found,
        edit it using either the default editor, or an alternate editor specified in *views*
        """
        if suffix != self.event:
            return

        x = event.x
        y = event.y

        # First determine what component or components we are going to hittest
        # on.  If our component is an Axis or PlotRenderer of any sort,
        # then that is the only candidate.  If our component is a container,
        # then we add its non-container components to the list of candidates;
        # any nested containers are lower priority than primary plot components.
        candidates = get_nested_components(
            self.component, [Container] + self.classes
        )

        # Hittest against all the candidate and take the first one
        item = None
        for candidate, offset in candidates:
            if candidate.is_in(x - offset[0], y - offset[1]):
                item = candidate
                break

        if item is not None:
            self.component.active_tool = self
            if item.__class__ in self.views:
                item.edit_traits(
                    kind="livemodal",
                    view=self.views[item.__class__],
                    parent=event.window.control,
                )
            else:
                item.edit_traits(kind="livemodal", parent=event.window.control)
            event.handled = True
            self.component.active_tool = None
            item.request_redraw()
