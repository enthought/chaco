# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# Major library imports
from numpy import array, asarray

# Enthought library imports
from enable.api import ColorTrait, MarkerTrait
from traits.api import Float, Int, Str
from traits.observation.events import TraitChangeEvent

# Local, relative imports
from chaco.abstract_overlay import AbstractOverlay
from chaco.chaco_traits import Optional
from chaco.plots.scatterplot import render_markers


class ScatterInspectorOverlay(AbstractOverlay):
    """
    Highlights points on a scatterplot as the mouse moves over them.
    Can render the points in a different style, as well as display a
    DataLabel.

    Used in conjuction with ScatterInspector.
    """

    #: The style to use when a point is hovered over
    hover_metadata_name = Str("hover")
    hover_marker = Optional(MarkerTrait)
    hover_marker_size = Optional(Int)
    hover_line_width = Optional(Float)
    hover_color = Optional(ColorTrait)
    hover_outline_color = Optional(ColorTrait)

    #: The style to use when a point has been selected by a click
    selection_metadata_name = Str("selections")
    selection_marker = Optional(MarkerTrait)
    selection_marker_size = Optional(Int)
    selection_line_width = Optional(Float)
    selection_color = Optional(ColorTrait)
    selection_outline_color = Optional(ColorTrait)

    # For now, implement the equivalent of this Traits 3 feature manually
    # using a series of trait change handlers (defined at the end of the
    # class)
    # @on_trait_change(
    #     'component.index.metadata_changed,component.value.metadata_changed'
    # )
    def metadata_updated(self, event):
        if self.component is not None:
            self.component.request_redraw()

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        plot = self.component
        if not plot or not plot.index or not getattr(plot, "value", True):
            return

        for inspect_type in (
            self.hover_metadata_name,
            self.selection_metadata_name,
        ):
            if inspect_type in plot.index.metadata:
                # if hasattr(plot,"value") and \
                #         not inspect_type in plot.value.metadata:
                #     continue
                index = plot.index.metadata.get(inspect_type, None)

                if index is not None and len(index) > 0:
                    index = asarray(index)
                    index_data = plot.index.get_data()

                    # Only grab the indices which fall within the data range.
                    index = index[index < len(index_data)]

                    # FIXME: In order to work around some problems with the
                    # selection model, we will only use the selection on the
                    # index.  The assumption that they are the same is
                    # implicit, though unchecked, already.
                    # value = plot.value.metadata.get(inspect_type, None)
                    value = index

                    if hasattr(plot, "value"):
                        value_data = plot.value.get_data()
                        screen_pts = plot.map_screen(
                            array([index_data[index], value_data[value]]).T
                        )
                    else:
                        screen_pts = plot.map_screen(index_data[index])

                    if inspect_type == self.selection_metadata_name:
                        prefix = "selection"
                    else:
                        prefix = "hover"
                    self._render_at_indices(gc, screen_pts, prefix)

    def _render_at_indices(self, gc, screen_pts, inspect_type):
        """ screen_pt should always be a list """
        self._render_marker_at_indices(gc, screen_pts, inspect_type)

    def _render_marker_at_indices(self, gc, screen_pts, prefix, sep="_"):
        """ screen_pt should always be a list """
        if len(screen_pts) == 0:
            return

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

            tmp = getattr(self, prefix + sep + valname)
            if tmp is not None:
                kwargs[attr] = tmp
            else:
                kwargs[attr] = getattr(plot, valname)

        # If the marker type is 'custom', we have to pass in the custom_symbol
        # kwarg to render_markers.
        if kwargs.get("marker", None) == "custom":
            kwargs["custom_symbol"] = plot.custom_symbol

        with gc:
            gc.clip_to_rect(plot.x, plot.y, plot.width, plot.height)
            render_markers(gc, screen_pts, **kwargs)

    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        self.overlay(self.component, gc, view_bounds, mode)

    def _component_changed(self, old, new):
        if old:
            old.observe(self._ds_changed, "index", remove=True)
            if hasattr(old, "value"):
                old.observe(self._ds_changed, "value", remove=True)
        if new:
            for dsname in ("index", "value"):
                if not hasattr(new, dsname):
                    continue
                new.observe(self._ds_changed, dsname)
                if getattr(new, dsname):
                    self._ds_changed(
                        TraitChangeEvent(
                            object=new,
                            name=dsname,
                            old=None,
                            new=getattr(new, dsname),
                        )
                    )

    def _ds_changed(self, event):
        old, new = event.old, event.new
        if old:
            old.observe(self.metadata_updated, "metadata_changed", remove=True)
        if new:
            new.observe(self.metadata_updated, "metadata_changed")
