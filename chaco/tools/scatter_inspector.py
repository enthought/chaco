""" Defines the ScatterInspector tool class.
"""

# Enthought library imports
from traits.api import Any, Bool, Enum, Event, HasStrictTraits, Str

# Local, relative imports
from .select_tool import SelectTool

HOVER_EVENT = "hover"

SELECT_EVENT = "select"

DESELECT_EVENT = "deselect"


class ScatterInspectorEvent(HasStrictTraits):
    #: Is it a hover event or a selection event?
    event_type = Enum([HOVER_EVENT, SELECT_EVENT, DESELECT_EVENT])

    #: What index was involved?
    event_index = Any


class ScatterInspector(SelectTool):
    """ A tool for inspecting scatter plots.

    It writes the index of the point under the cursor to the metadata of the
    index and value data sources, and allows clicking to select the point.
    Other components can listen for metadata updates on the data sources.

    By default, it writes the index of the point under the cursor to the
    "hover" key in metadata, and the index of a clicked point to "selection".
    """

    #: If persistent_hover is False, then a point will be de-hovered as soon as
    #: the mouse leaves its hit-testing area. If persistent_hover is True, then
    #: a point does no de-hover until another point get hover focus.
    persistent_hover = Bool(False)

    #: The names of the data source metadata for hover and selection events.
    hover_metadata_name = Str('hover')
    selection_metadata_name = Str('selections')

    #: This tool emits events when hover or selection changes
    inspector_event = Event(ScatterInspectorEvent)

    # -------------------------------------------------------------------------
    # Override/configure inherited traits
    # -------------------------------------------------------------------------

    #: This tool is not visible
    visible = False

    #: This tool does not have a visual representation
    draw_mode = "none"

    def normal_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'normal' state.

        If the cursor is within **threshold** of a data point, the method
        writes the index to the plot's data sources' "hover" metadata.

        This method emits a ScatterInspectorEvent when a new scatter point is
        hovered over and when the mouse leaves that point.
        """
        plot = self.component
        index = plot.map_index((event.x, event.y), threshold=self.threshold)
        insp_event = ScatterInspectorEvent(event_type=HOVER_EVENT,
                                           event_index=index)
        if index is not None:
            old = plot.index.metadata.get(self.hover_metadata_name, None)
            plot.index.metadata[self.hover_metadata_name] = [index]
            if old != [index]:
                self.inspector_event = insp_event
            if hasattr(plot, "value"):
                plot.value.metadata[self.hover_metadata_name] = [index]
        elif not self.persistent_hover:
            old = plot.index.metadata.pop(self.hover_metadata_name, None)
            if old:
                self.inspector_event = insp_event
            if hasattr(plot, "value"):
                plot.value.metadata.pop(self.hover_metadata_name, None)

        return

    def _get_selection_state(self, event):
        plot = self.component
        index = plot.map_index((event.x, event.y), threshold=self.threshold)

        already_selected = False
        for name in ('index', 'value'):
            if not hasattr(plot, name):
                continue
            md = getattr(plot, name).metadata
            if md is None or self.selection_metadata_name not in md:
                continue
            if index in md[self.selection_metadata_name]:
                already_selected = True
                break
        return already_selected, (index is not None)

    def _get_selection_token(self, event):
        plot = self.component
        index = plot.map_index((event.x, event.y), threshold=self.threshold)
        return index

    def _deselect(self, index=None):
        """ Deselects a particular index.  If no index is given, then
        deselects all points.
        """
        plot = self.component
        insp_event = ScatterInspectorEvent(event_type=DESELECT_EVENT,
                                           event_index=index)
        for name in ('index', 'value'):
            if not hasattr(plot, name):
                continue
            md = getattr(plot, name).metadata
            if self.selection_metadata_name not in md:
                pass
            elif index in md[self.selection_metadata_name]:
                new_list = md[self.selection_metadata_name][:]
                new_list.remove(index)
                md[self.selection_metadata_name] = new_list
                # Only issue 1 event:
                if name == 'index':
                    self.inspector_event = insp_event
        return

    def _select(self, index, append=True):
        plot = self.component
        insp_event = ScatterInspectorEvent(event_type=SELECT_EVENT,
                                           event_index=index)
        for name in ('index', 'value'):
            if not hasattr(plot, name):
                continue
            md = getattr(plot, name).metadata
            selection = md.get(self.selection_metadata_name, None)

            # If no existing selection
            if selection is None:
                md[self.selection_metadata_name] = [index]
            # check for list-like object supporting append
            else:
                if append:
                    if index not in md[self.selection_metadata_name]:
                        new_list = md[self.selection_metadata_name] + [index]
                        md[self.selection_metadata_name] = new_list
                        # Manually trigger the metadata_changed event on
                        # the datasource. Datasources only automatically
                        # fire notifications when the values inside the
                        # metadata dict change, but they do not listen
                        # for further changes on those values.
                        # DEPRECATED: use self.inspector_event instead:
                        getattr(plot, name).metadata_changed = True
                else:
                    md[self.selection_metadata_name] = [index]

            # Test to only issue 1 event per selection, not 1 per axis:
            if name == 'index':
                self.inspector_event = insp_event

        return


# EOF
