""" Defines the PlotSession class.
"""



# Enthoght library imports
from chaco.array_plot_data import ArrayPlotData
from chaco.default_colormaps import *
from traits.api import Any, Bool, Dict, HasTraits, Instance, Int, \
                                 List, Property, Trait, Str


# Local, relative imports
from .plot_window import PlotWindow
from .preferences import Preferences


class PlotSession(HasTraits):
    """
    Encapsulates all of the session-level globals, including preferences,
    windows, etc.
    """

    # The preferences object in effect for this session.
    prefs = Instance(Preferences, args=())

    # The list of currently active windows.
    windows = List(PlotWindow)

    # A dict mapping names to windows.
    window_map = Dict(Str, PlotWindow)

    # The current hold state.
    hold = Bool(False)

    # The session holds a single ArrayPlotData instance to which it adds unnamed
    # arrays that are provided to various plotting commands.
    data = Instance(ArrayPlotData, args=())


    #------------------------------------------------------------------------
    # "active" pointers
    #------------------------------------------------------------------------

    # The index of the active window.
    active_window_index = Trait(None, None, Int)

    # The active window.
    active_window = Property

    # The active colormap.
    colormap = Trait(jet, Any)


    def new_window(self, name=None, title=None, is_image=False):
        """Creates a new window and returns the index into the **windows** list
        for the new window.
        """
        new_win = PlotWindow(
            is_image=is_image,
            size=(self.prefs.window_width, self.prefs.window_height),
            bgcolor=self.prefs.bgcolor,
            image_default_origin=self.prefs.image_default_origin,
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
        return len(self.windows)-1

    def get_window(self, ident):
        """ Retrieves a window either by index or by name """
        if isinstance(ident, str):
            return self.window_map.get(ident, None)
        elif type(ident) == int and ident < len(self.windows):
            return self.windows[ident]
        else:
            return None

    def del_window(self, ident):
        """ Deletes the specified window.

        Parameters
        ----------
        ident : string or number
            The name of the window in **window_map**, or the index of the
            window in **windows**.
        """
        if isinstance(ident, str):
            if ident in self.window_map:
                win = self.window_map[ident]
                del self.window_map[ident]
            else:
                return
        elif type(ident) == int:
            if ident >= len(self.windows):
                print("No such window %d." % ident)

            win = self.windows.pop(ident)
            if len(self.windows) == 0:
                self.active_window = None
            elif self.active_window_index >= ident:
                self.active_window_index -= 1

            if win in self.window_map.values():
                # we have to go through the whole dict and remove all keys
                # that correspond to the deleted window
                for k, v in list(self.window_map.items()):
                    if v == win:
                        del self.window_map[k]
        else:
            return

    def _get_active_window(self):
        if self.active_window_index is not None:
            return self.windows[self.active_window_index]
        else:
            return None

    def _set_active_window(self, win):
        if win in self.windows:
            self.active_window_index = self.windows.index(win)
        elif win is None:
            self.active_window_index = None
        else:
            raise RuntimeError("That window is not part of this session.")

    def _colormap_changed(self):
        plots = []
        for w in self.windows:
            container = w.get_container()
            for vals in container.plots.values():
                plots.extend(vals)
        for p in plots:
            if hasattr(p, "color_mapper"):
                p.color_mapper = self.colormap(p.color_mapper.range)
                p.invalidate_draw()
                p.request_redraw()
            elif hasattr(p, "colors"):
                if isinstance(p.colors, str) or \
                   isinstance(p.colors, AbstractColormap):
                    p.colors = color_map_dict[self.colormap]


# EOF
