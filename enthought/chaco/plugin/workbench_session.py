""" A Chaco Shell PlotSession which raises Workbench Editors instead of
free-standing windows.
"""

from enthought.traits.api import Any, Dict, List, Str
from enthought.chaco.shell.session import PlotSession

from plot_editor import PlotEditor


class WorkbenchSession(PlotSession):
    """ A Chaco Shell PlotSession which raises Workbench Editors instead of
    free-standing windows.
    """

    # The Envisage Application we are in.
    application = Any()

    # The list of currently active windows.
    windows = List()

    # A dict mapping names to windows.
    window_map = Dict(Str, Any)

    def new_window(self, name=None, title=None, is_image=False):
        """Creates a new window and returns the index into the **windows** list
        for the new window.
        """
        workbench = self.application.get_service(
            'enthought.envisage.ui.workbench.workbench.Workbench')
        new_win = PlotEditor(
            is_image=is_image,
            size=(self.prefs.window_width, self.prefs.window_height),
            bgcolor=self.prefs.bgcolor,
            image_default_origin=self.prefs.image_default_origin,
            window=workbench.active_window,
        )
        new_win.data = self.data
        new_win.get_container().data = self.data
        new_win.session = self

        if title is not None:
            new_win.set_title(title)
        elif name != None:
            new_win.set_title(name)
        else:
            new_win.set_title(self.prefs.default_window_name)

        self.windows.append(new_win)
        if name != None:
            self.window_map[name] = new_win

        workbench.active_window.add_editor(new_win)
        workbench.active_window.activate_editor(new_win)

        return len(self.windows)-1


