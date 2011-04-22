""" Defines the BasePlotFrame class (deprecated).
"""

#################################################################################
#
# NOTE: PlotFrames are deprecated.  There is no need to use them any more.
# This class will be removed some time in the near future.
#
#################################################################################

from __future__ import with_statement

# Enthought library imports
from enable.api import Container
from traits.api import Enum

# Local, relative imports
from plot_component import PlotComponent, DEFAULT_DRAWING_ORDER


class BasePlotFrame(Container, PlotComponent):
    """
    Base class for plot frames.  Primarily defines the basic functionality
    of managing slots (sub-containers) within the plot frame.

    NOTE: PlotFrames are deprecated. There is no need to use them any more.
    This class will be removed some time in the near future.
    """

    # A named list of places/positions/"slots" on the frame where PlotComponents
    # can place themselves.  Subclasses must redefine this trait with the
    # appropriate values.  Note that by default, __getattr__ treats these
    # slot names as attributes on the class so they can be directly accessed.
    # This is a class attribute.
    slot_names = ()

    # Dimensions in which this frame can resize to fit its components.
    # This is similar to the **resizable** trait on PlotComponent. Chaco
    # plot frames use this attribute in preference to the Enable
    # **auto_size** attribute (which is overridden to be False by default).
    fit_components = Enum("", "h", "v", "hv")

    # Overrides the Enable auto_size trait (which will be deprecated in the future)
    auto_size = False

    draw_order = DEFAULT_DRAWING_ORDER

    def __init__(self, **kw):
        self._frame_slots = {}
        super(BasePlotFrame, self).__init__(**kw)
        return

    def add_to_slot(self, slot, component, stack="overlay"):
        """
        Adds a component to the named slot using the given stacking mode.
        The valid modes are: 'overlay', 'left', 'right', 'top', 'bottom'.
        """
        self.frame_slots[slot].add_plot_component(component, stack)
        return

    def set_slot(self, slotname, container):
        """
        Sets the named slot to use the given container. *container* can be None.
        """
        if self._frame_slots.has_key(slotname):
            old_container = self._frame_slots[slotname]
            Container.remove(self, old_container)
        if container is not None:
            self._frame_slots[slotname] = container
            Container.add(self, container)
        return

    def get_slot(self, slotname):
        """ Returns the container in the named slot. """
        return self._frame_slots.get(slotname, None)

    #------------------------------------------------------------------------
    # PlotComponent interface
    #------------------------------------------------------------------------

    def draw(self, gc, view_bounds=None, mode="normal"):
        """ Draws the plot frame.

        Frames are the topmost Chaco component that knows about layout, and they
        are the start of the layout pipeline.  When they are asked to draw,
        they can assume that their own size has been set properly and this in
        turn drives the layout of the contained components within the trame.
        """
        self.do_layout()

        #if gc.window and gc.window.is_sizing:
        if 0:
            with gc:
                gc.translate_ctm(*self.position)
                #TODO: We are ignoring Container...
                PlotComponent.draw(self, gc, view_bounds, "interactive")
        else:
            super(BasePlotFrame, self).draw(gc, view_bounds, mode)
        return

    def do_layout(self, size=None, force=False):
        """ Tells this frame to do layout at a given size.

        Overrides PlotComponent. If this frame needs to fit components in at
        least one dimension, then it checks whether any of them need to do
        layout; if so, the frame needs to do layout also.
        """
        if not self._layout_needed and not force and self.fit_components != "":
            for slot in self._frame_slots.values():
                if slot._layout_needed:
                    self._layout_needed = True
                    break
        return PlotComponent.do_layout(self, size, force)

    def _draw(self, *args, **kw):
        """ Draws the plot frame.

        Overrides PlotComponent and Container, explicitly calling the
        PlotComponent version of _draw().
        """
        PlotComponent._draw(self, *args, **kw)
        return

    def _dispatch_to_enable(self, event, suffix):
        """ Calls Enable-level event handlers.

        Overrides PlotComponent.
        """
        Container.dispatch(self, event, suffix)
        return

    #------------------------------------------------------------------------
    # Event handlers, properties
    #------------------------------------------------------------------------

    def _bounds_changed(self, old, new):
        if self.container is not None:
            self.container._component_bounds_changed(self)
        self._layout_needed = True
        return

    def _bounds_items_changed(self, event):
        return self._bounds_changed(None, self.bounds)

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def __getattr__(self, name):
        if name in self.slot_names:
            return self._frame_slots[name]
        else:
            raise AttributeError, "'%s' object has no attribute '%s'" % \
                                    (self.__class__.__name__, name)

    def __setattr__(self, name, value):
        if name in self.slot_names:
            self.set_slot(name, value)
        else:
            super(BasePlotFrame, self).__setattr__(name, value)
        return

    ### Persistence ###########################################################
#    _pickles = ("_frame_slots", "_components", "fit_components", "fit_window")

    def post_load(self, path=None):
        super(BasePlotFrame, self).post_load(path)
        for slot in self._frame_slots.values():
            slot.post_load(path)
        return


# EOF
