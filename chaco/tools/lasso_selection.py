# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the LassoSelection controller class.
"""
# Major library imports
import numpy
from numpy import array, column_stack, empty, sometrue, vstack, zeros

# Enthought library imports
from traits.api import (
    Any,
    Array,
    Enum,
    Event,
    Bool,
    Instance,
    Property,
    Str,
    Trait,
    List,
)
from kiva.api import points_in_polygon

# Chaco imports
from chaco.abstract_controller import AbstractController
from chaco.abstract_data_source import AbstractDataSource
from chaco.base_xy_plot import BaseXYPlot
from chaco.base_2d_plot import Base2DPlot


class LassoSelection(AbstractController):
    """A controller that represents the interaction of "lassoing" a set of
    points.

    "Lassoing" means drawing an arbitrary selection region around the points
    by dragging the mouse along the outline of the region.
    """

    #: An Nx2 array of points in data space representing all selected points.
    dataspace_points = Property(Array)

    #: A list of all the selection polygons.
    disjoint_selections = Property(List)

    #: Fires whenever **dataspace_points** changes, necessitating a redraw of the
    #: selection region.
    updated = Event

    #: Fires when the selection mask changes.
    selection_changed = Event

    #: Fires when the user release the mouse button and finalizes the selection.
    selection_completed = Event

    #: If True, the selection mask is updated as the mouse moves, rather
    #: than only at the beginning and end of the selection operation.
    incremental_select = Bool(False)

    #: The selection mode of the lasso pointer: "include", "exclude" or
    #: "invert" points from the selection. The "include" and "exclude"
    #: settings essentially invert the selection mask. The "invert" setting
    #: differs from "exclude" in that "invert" inverses the selection of all
    #: points the the lasso'ed polygon, while "exclude" operates only on
    #: points included in a previous selection.
    selection_mode = Enum("include", "exclude", "invert")

    #: The data source that the mask of selected points is attached to.  Note
    #: that the indices in this data source must match the indices of the data
    #: in the plot.
    selection_datasource = Instance(AbstractDataSource)

    #: The name of the metadata on the datasource that we will write
    #: the selection mask to
    metadata_name = Str("selection")

    #: Mapping from screen space to data space. By default, it is just
    #: self.component.
    plot = Property

    #: The button which this tool responds to
    drag_button = Enum("left", "right")

    #: The possible event states of this selection tool (overrides
    #: enable.Interactor).
    #:
    #: normal:
    #:     Nothing has been selected, and the user is not dragging the mouse.
    #: selecting:
    #:     The user is dragging the mouse and is actively changing the
    #:     selection region.
    event_state = Enum("normal", "selecting")

    # ----------------------------------------------------------------------
    # Private Traits
    # ----------------------------------------------------------------------

    # The PlotComponent associated with this tool.
    _plot = Trait(None, Any)

    # To support multiple selections, a list of cached selections and the
    # active selection are maintained. A single list is not used because the
    # active selection is re-created every time a new point is added via
    # the vstack function.
    _active_selection = Array
    _previous_selections = List(Array)

    # ----------------------------------------------------------------------
    # Properties
    # ----------------------------------------------------------------------

    def _get_dataspace_points(self):
        """Returns a complete list of all selected points.

        This property exists for backwards compatibility, as the
        disjoint_selections property is almost always the preferred
        method of accessingselected points
        """
        composite = empty((0, 2))
        for region in self.disjoint_selections:
            if len(region) > 0:
                composite = vstack((composite, region))

        return composite

    def _get_disjoint_selections(self):
        """Returns a list of all disjoint selections composed of
        the previous selections and the active selection
        """
        if len(self._active_selection) == 0:
            return self._previous_selections
        else:
            return self._previous_selections + [self._active_selection]

    # ----------------------------------------------------------------------
    # Event Handlers
    # ----------------------------------------------------------------------

    def normal_left_down(self, event):
        if self.drag_button == "left":
            return self.normal_mouse_down(event)

    def normal_right_down(self, event):
        if self.drag_button == "right":
            return self.normal_mouse_down(event)

    def normal_mouse_down(self, event):
        """Handles the left mouse button being pressed while the tool is
        in the 'normal' state.

        Puts the tool into 'selecting' mode, and starts defining the selection.
        """
        # We may want to generalize this for the n-dimensional case...

        self._active_selection = empty((0, 2), dtype=numpy.bool)

        if self.selection_datasource is not None:
            self.selection_datasource.metadata[self.metadata_name] = zeros(
                len(self.selection_datasource.get_data()), dtype=numpy.bool
            )
        self.selection_mode = "include"
        self.event_state = "selecting"
        self.selecting_mouse_move(event)

        if (not event.shift_down) and (not event.control_down):
            self._previous_selections = []
        else:
            if event.control_down:
                self.selection_mode = "exclude"
            else:
                self.selection_mode = "include"
        self.trait_property_changed(
            "disjoint_selections", [], self.disjoint_selections
        )

    def selecting_left_up(self, event):
        if self.drag_button == "left":
            return self.selecting_mouse_up(event)

    def selecting_right_up(self, event):
        if self.drag_button == "right":
            return self.selecting_mouse_up(event)

    def selecting_mouse_up(self, event):
        """Handles the mouse button coming up in the 'selecting' state.

        Completes the selection and switches to the 'normal' state.
        """
        self.event_state = "normal"
        self.selection_completed = True
        self._update_selection()

        self._previous_selections.append(self._active_selection)
        self._active_selection = empty((0, 2), dtype=numpy.bool)

    def selecting_mouse_move(self, event):
        """Handles the mouse moving when the tool is in the 'selecting' state.

        The selection is extended to the current mouse position.
        """
        # Translate the event's location to be relative to this container
        xform = self.component.get_event_transform(event)
        event.push_transform(xform, caller=self)
        new_point = self._map_data(array((event.x, event.y)))
        self._active_selection = vstack(
            (self._active_selection, array((new_point,)))
        )
        self.updated = True
        if self.incremental_select:
            self._update_selection()
        # Report None for the previous selections
        self.trait_property_changed("disjoint_selections", None)

    def selecting_mouse_leave(self, event):
        """Handles the mouse leaving the plot when the tool is in the
        'selecting' state.

        Ends the selection operation.
        """
        # Treat this as if it were a selecting_mouse_up event
        return self.selecting_mouse_up(event)

    def normal_key_pressed(self, event):
        """Handles the user pressing a key in the 'normal' state.

        If the user presses the Escape key, the tool is reset.
        """
        if event.character == "Esc":
            self._reset()
        elif event.character == "a" and event.control_down:
            self._reset()
            self._select_all()
        elif event.character == "i" and event.control_down:
            self.selecting_mouse_up(None)
            self.selection_mode = "invert"
            self._select_all()

    # ----------------------------------------------------------------------
    # Protected Methods
    # ----------------------------------------------------------------------

    def _dataspace_points_default(self):
        return empty((0, 2), dtype=numpy.bool)

    def _reset(self):
        """Resets the selection"""
        self.event_state = "normal"
        self._active_selection = empty((0, 2), dtype=numpy.bool)
        self._previous_selections = []
        self._update_selection()

    def _select_all(self):
        """Selects all points in the plot. This is done by making a rectangle
        using the corners of the plot, which is simple but effective. A
        much cooler, but more time-intensive solution would be to make
        a selection polygon representing the convex hull.
        """
        points = [
            self._map_data(array((self.plot.x, self.plot.y2))),
            self._map_data(array((self.plot.x2, self.plot.y2))),
            self._map_data(array((self.plot.x2, self.plot.y))),
            self._map_data(array((self.plot.x, self.plot.y))),
        ]

        self._active_selection = numpy.array(points)
        self._update_selection()

    def _update_selection(self):
        """Sets the selection datasource's metadata to a mask of all
        the points selected
        """
        if self.selection_datasource is None:
            return

        selected_mask = zeros(
            self.selection_datasource._data.shape, dtype=numpy.bool
        )
        data = self._get_data()

        # Compose the selection mask from the cached selections first, then
        # the active selection, taking into account the selection mode only
        # for the active selection

        for selection in self._previous_selections:
            selected_mask |= points_in_polygon(data, selection, False).astype(
                bool, copy=False
            )

        active_selection = points_in_polygon(
            data, self._active_selection, False
        ).astype(bool, copy=False)

        if self.selection_mode == "exclude":
            # XXX I think this should be "set difference"? - CJW
            selected_mask |= active_selection
            selected_mask = ~selected_mask

        elif self.selection_mode == "invert":
            selected_mask ^= active_selection
        else:
            selected_mask |= active_selection

        if sometrue(
            selected_mask
            != self.selection_datasource.metadata[self.metadata_name]
        ):
            self.selection_datasource.metadata[
                self.metadata_name
            ] = selected_mask
            self.selection_changed = True

    def _map_screen(self, points):
        """Maps a point in data space to a point in screen space on the plot.

        Normally this method is a pass-through, but it may do more in
        specialized plots.
        """
        return self.plot.map_screen(points)[:, :2]

    def _map_data(self, point):
        """Maps a point in screen space to data space.

        Normally this method is a pass-through, but for plots that have more
        data than just (x,y), proper transformations need to happen here.
        """
        if isinstance(self.plot, Base2DPlot):
            # Base2DPlot.map_data takes an array of points, for some reason
            return self.plot.map_data([point])[0]
        elif isinstance(self.plot, BaseXYPlot):
            return self.plot.map_data(point, all_values=True)[:2]
        else:
            raise RuntimeError(
                "LassoSelection only supports BaseXY and Base2D plots"
            )

    def _get_data(self):
        """Returns the datapoints in the plot, as an Nx2 array of (x,y)."""
        return column_stack(
            (self.plot.index.get_data(), self.plot.value.get_data())
        )

    # ------------------------------------------------------------------------
    # Property getter/setters
    # ------------------------------------------------------------------------

    def _get_plot(self):
        if self._plot is not None:
            return self._plot
        else:
            return self.component

    def _set_plot(self, val):
        self._plot = val
