
# Major library imports
from numpy import array

# Enthought library imports
from enthought.enable2.api import BaseTool, ColorTrait
from enthought.traits.api import Enum, Float, Instance, Int, Trait

# Local, relative imports
from abstract_overlay import AbstractOverlay
from scatter_markers import marker_trait
from scatterplot import render_markers

class ScatterInspectorOverlay(AbstractOverlay):
    """
    Highlights points on a scatterplot as the mouse moves over them.
    Can render the points in a different style, as well as display a
    DataLabel.

    Used in conjuction with ScatterInspector.
    """

    # The style to use when a point is hovered over
    hover_marker = Trait(None, None, marker_trait)
    hover_marker_size = Trait(None, None, Int)
    hover_line_width = Trait(None, None, Float)
    hover_color = Trait(None, None, ColorTrait)
    hover_outline_color = Trait(None, None, ColorTrait)

    # The style to use when a point has been selected by a click
    selection_marker = Trait(None, None, marker_trait)
    selection_marker_size = Trait(None, None, Int)
    selection_line_width = Trait(None, None, Float)
    selection_color = Trait(None, None, ColorTrait)
    selection_outline_color = Trait(None, None, ColorTrait)

    # For now, implement the equivalent of this Traits 3 feature manually
    # using a series of trait change handlers (defined at the end of the
    # class)
    #@on_trait_change('component.index.metadata_changed,component.value.metadata_changed')
    def metadata_changed(self, object, name, old, new):
        if self.component is not None:
            self.component.request_redraw()
        return

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        plot = self.component
        if not plot or not plot.index or not plot.value:
            return

        for inspect_type in ('hover', 'selections'):
            if inspect_type in plot.index.metadata and inspect_type in plot.value.metadata:
                index = plot.index.metadata.get(inspect_type, None)
                value = plot.value.metadata.get(inspect_type, None)
                # TODO: need to improve handling of cases when len(index) != len(value)
                if index is not None and value is not None:
                    if len(index) == 0 and len(value) == 0:
                        continue
                    screen_pts = plot.map_screen(array((plot.index.get_data()[index],
                                                       plot.value.get_data()[value])).T)

                    # Hmm.. this is a little klunky, but I prefer for the visual
                    # appearance traits to be named "selection_*" and the metadata
                    # name should be "selections", and so we have to bridge
                    # the difference here.
                    if inspect_type == "selections":
                        prefix = "selection"
                    else:
                        prefix = "hover"
                    self._render_at_indices(gc, screen_pts, prefix)
        return

    def _render_at_indices(self, gc, screen_pts, inspect_type):
        """ screen_pt should always be a list """
        self._render_marker_at_indices(gc, screen_pts, inspect_type)

    def _render_marker_at_indices(self, gc, screen_pts, prefix, sep="_"):
        """ screen_pt should always be a list """
        plot = self.component

        mapped_attribs = ("color", "outline_color", "marker")
        other_attribs = ("marker_size", "line_width")
        kwargs = {}
        for attr in mapped_attribs + other_attribs:
            if attr in mapped_attribs:
                # Resolve the mapped trait
                valname = attr + "_"
            else:
                valname = attr

            tmp = getattr(self, prefix+sep+valname)
            if tmp is not None:
                kwargs[attr] = tmp
            else:
                kwargs[attr] = getattr(plot, valname)

        # If the marker type is 'custom', we have to pass in the custom_symbol
        # kwarg to render_markers.
        if kwargs.get("marker", None) == "custom":
            kwargs["custom_symbol"] = plot.custom_symbol

        gc.save_state()
        gc.clip_to_rect(plot.x, plot.y, plot.width, plot.height)
        render_markers(gc, screen_pts, **kwargs)
        gc.restore_state()


    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        self.overlay(self.component, gc, view_bounds, mode)

    def _component_changed(self, old, new):
        if old:
            old.on_trait_change(self._ds_changed, 'index', remove=True)
            old.on_trait_change(self._ds_changed, 'value', remove=True)
        if new:
            new.on_trait_change(self._ds_changed, 'index')
            new.on_trait_change(self._ds_changed, 'value')
            if new.index:
                self._ds_changed(new, 'index', None, new.index)
            if new.value:
                self._ds_changed(new, 'value', None, new.value)
        return

    def _ds_changed(self, object, name, old, new):
        if old:
            old.on_trait_change(self.metadata_changed, 'metadata_changed', remove=True)
        if new:
            new.on_trait_change(self.metadata_changed, 'metadata_changed')
        return


