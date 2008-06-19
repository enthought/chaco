""" Defines the ScatterInspector tool class.
"""

# Enthought library imports
from enthought.enable2.api import BaseTool, KeySpec
from enthought.traits.api import Any, Bool, Enum, Float, Instance, Str

# Chaco imports
from enthought.chaco2.api import ScatterPlot


class ScatterInspector(BaseTool):
    """ A tool for inspecting scatter plots. 
    
    It writes the index of the point under the cursor to the metadata of the 
    index and value data sources, and allows clicking to select the point. 
    Other components can listen for metadata updates on the data sources.
    
    By default, it writes the index of the point under the cursor to the "hover"
    key in metadata, and the index of a clicked point to "selection".
    """

    # The threshold, in pixels, around the cursor location to search for points.
    threshold = Float(5.0)

    # How selections are handled
    #   "toggle": The user clicks on points (while optionally holding down a 
    #             modifier key) to select or deselect them.  If the point is
    #             already selected, clicking it again deselects it.  The
    #             modifier key to use is set by **multiselect_modifier**.  The
    #             only way to deselect points is by clicking on them; clicking
    #             on a screen space outside of the plot will not deselect points.
    #   "multi":  Like **toggle** mode, except that the user can deselect all
    #             points at once by clicking on the plot area away from a point.
    #   "single": The user can only select a single point at a time.  
    #   "off":    The user cannot select points via clicking.
    selection_mode = Enum("toggle", "multi", "single", "off")

    # The modifier key to use to multi-select points.  Only used in **toggle**
    # and **multi** selection modes.
    multiselect_modifier = Instance(KeySpec, args=(None, "control"), allow_none=True)

    # If persistent_hover is False, then a point will be de-hovered as soon as
    # the mouse leaves its hittesting area.  If persistent_hover is True, then
    # a point does no de-hover until another point get hover focus.
    persistent_hover = Bool(False)

    #------------------------------------------------------------------------
    # Override/configure inherited traits
    #------------------------------------------------------------------------
    
    # This tool is not visible
    visible = False

    # This tool does not have a visual reprentation
    draw_mode = "none"

    def normal_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'normal' state.
        
        If the cursor is within **threshold** of a data point, the method 
        writes the index to the plot's data sources' "hover" metadata.
        """
        plot = self.component
        index = plot.map_index((event.x, event.y), threshold=self.threshold)
        if index:
            plot.index.metadata["hover"] = [index]
            plot.value.metadata["hover"] = [index]
        elif not self.persistent_hover:
            plot.index.metadata.pop("hover", None)
            plot.value.metadata.pop("hover", None)
        return
    
    def normal_left_down(self, event):
        """ Handles the left mouse button being pressed when the tool is in the
        'normal' state.
        
        If selecting is enabled and the cursor is within **threshold** of a
        data point, the method writes the index to the plot's data sources'
        "selection" metadata.
        """
        if self.selection_mode != "off":
            plot = self.component
            index = plot.map_index((event.x, event.y), threshold=self.threshold)
            index_md = plot.index.metadata.get("selections", None)
            value_md = plot.value.metadata.get("selections", None)
            
            already_selected = False
            for name in ('index', 'value'):
                md = getattr(plot, name).metadata
                if md is None or "selections" not in md:
                    continue
                if index in md["selections"]:
                    already_selected = True
                    break

            modifier_down = self.multiselect_modifier.match(event)

            if (self.selection_mode == "single") or\
                    (self.selection_mode == "multi" and not modifier_down):
                if index is not None and not already_selected:
                    if self.selection_mode == "single":
                        self._select(index, append=False)
                    else:
                        self._select(index, append=True)
                    event.handled = True
                else:
                    self._deselect(index)

            else:  # multi or toggle
                if index is not None:
                    if already_selected:
                        self._deselect(index)
                    else:
                        self._select(index)
                    event.handled = True
            return

    def _deselect(self, index=None):
        """ Deselects a particular index.  If no index is given, then
        deselects all points.
        """
        plot = self.component
        for name in ('index', 'value'):
            md = getattr(plot, name).metadata
            if not "selections" in md:
                pass
            elif index in md["selections"]:
                md["selections"].remove(index)
                getattr(plot, name).metadata_changed = True
        return

    def _select(self, index, append=True):
        plot = self.component
        for name in ('index', 'value'):
            md = getattr(plot, name).metadata
            selection = md.get("selections", None)

            # If no existing selection
            if selection is None:
                md["selections"] = [index]
            # check for list-like object supporting append
            else:
                if append:
                    if index not in md["selections"]:
                        md["selections"].append(index)
                        # Manually trigger the metadata_changed event on
                        # the datasource.  Datasources only automatically
                        # fire notifications when the values inside the
                        # metadata dict change, but they do not listen
                        # for further changes on those values.
                        getattr(plot, name).metadata_changed = True
                else:
                    md["selections"] = [index]
        return


# EOF
