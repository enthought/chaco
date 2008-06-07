
# Enthought library imports
from enthought.enable2.api import BaseTool, ColorTrait
from enthought.traits.api import on_trait_change, Float, Int, Trait

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

    @on_trait_change('component.index.metadata_changed,component.value.metadata_changed')
    def metadata_changed(self, object, name, old, new):
        if self.component is not None:
            self.component.request_redraw()
        return

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        plot = self.component
        if not plot or not plot.index or not plot.value:
            return

        for name in ('hover', 'selection'):
            if name in plot.index.metadata and name in plot.value.metadata:
                index_ndx = plot.index.metadata.get(name, None)
                value_ndx = plot.value.metadata.get(name, None)
                screen_pt = plot.map_screen((plot.index.get_data()[index_ndx],
                                             plot.value.get_data()[value_ndx]))

                self._render_at_data_indices(gc, screen_pt, name)
        return

    def _render_at_data_indices(self, gc, screen_pt, prefix, sep="_"):
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

        render_markers(gc, [screen_pt], **kwargs)


    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        self.overlay(self.component, gc, view_bounds, mode)


