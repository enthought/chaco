
from enthought.chaco2.api import BaseTool
from enthought.traits.api import Dict, List

class BroadcasterTool(BaseTool):
    """ Simple tool that keeps a list of other tools, and broadcasts events it
    receives to all of the tools.
    """

    tools = List

    mouse_owners = Dict

    def dispatch(self, event, suffix):
        handled = False   # keeps track of whether any tool handled this event

        if event.window.mouse_owner == self:
            tools = self.mouse_owners.keys()
            mouse_owned = True
        else:
            tools = self.tools
            mouse_owned = False

        for tool in tools:
            if mouse_owned:
                event.window.set_mouse_owner(tool, self.mouse_owners[tool])

            tool.dispatch(event, suffix)
            if event.handled:
                handled = True
                event.handled = False

            if mouse_owned and event.window.mouse_owner is None:
                # The tool owned the mouse before handling the previous event,
                # and now doesn't, so remove it from the list of mouse_owners
                del self.mouse_owners[tool]

            elif not mouse_owned and event.window.mouse_owner == tool:
                # The tool is a new mouse owner
                self.mouse_owners[tool] = event.window.mouse_owner_transform

        if len(self.mouse_owners) == 0:
            if event.window.mouse_owner == self:
                event.window.set_mouse_owner(None)
        else:
            event.window.set_mouse_owner(self, event.net_transform())

        event.handled = handled
