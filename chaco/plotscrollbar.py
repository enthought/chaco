from traits.api import Any, Enum, Int, Property, Trait

from enable.api import NativeScrollBar


class PlotScrollBar(NativeScrollBar):
    """
    A ScrollBar that can be wired up to anything with an xrange or yrange
    and which can be attached to a plot container.
    """

    # The axis corresponding to this scrollbar.
    axis = Enum("index", "value")

    # The renderer or Plot to attach this scrollbar to.  By default, this
    # is just self.component.
    plot = Property

    # The mapper for associated with the scrollbar. By default, this is the
    # mapper on **plot** that corresponds to **axis**.
    mapper = Property

    # ------------------------------------------------------------------------
    # Private traits
    # ------------------------------------------------------------------------

    # The value of the override plot to use, if any.  If None, then uses
    # self.component.
    _plot = Trait(None, Any)

    # The value of the override mapper to use, if any.  If None, then uses the
    # mapper on self.component.
    _mapper = Trait(None, Any)

    # Stores the index (0 or 1) corresponding to self.axis
    _axis_index = Trait(None, None, Int)

    # ----------------------------------------------------------------------
    # Public methods
    # ----------------------------------------------------------------------

    def force_data_update(self):
        """This forces the scrollbar to recompute its range bounds.  This
        should be used if datasources are changed out on the range, or if
        the data ranges on existing datasources of the range are changed.
        """
        self._handle_dataspace_update()

    def overlay(self, component, gc, view_bounds=None, mode="default"):
        self.do_layout()
        self._draw_mainlayer(gc, view_bounds, "default")

    def _draw_plot(self, gc, view_bounds=None, mode="default"):
        self._draw_mainlayer(gc, view_bounds, "default")

    def _do_layout(self):
        if getattr(self.plot, "_layout_needed", False):
            self.plot.do_layout()
        axis = self._determine_axis()
        low, high = self.mapper.screen_bounds
        self.bounds[axis] = high - low
        self.position[axis] = low
        self._widget_moved = True

    def _get_abs_coords(self, x, y):
        if self.container is not None:
            return self.container.get_absolute_coords(x, y)
        else:
            return self.component.get_absolute_coords(x, y)

    # ----------------------------------------------------------------------
    # Scrollbar
    # ----------------------------------------------------------------------

    def _handle_dataspace_update(self):
        # This method reponds to changes from the dataspace side, e.g.
        # a change in the range bounds or the data bounds of the datasource.

        # Get the current datasource bounds
        range = self.mapper.range
        bounds_list = [
            source.get_bounds()
            for source in range.sources
            if source.get_size() > 0
        ]
        mins, maxes = zip(*bounds_list)
        dmin = min(mins)
        dmax = max(maxes)

        view = float(range.high - range.low)

        # Take into account the range's current low/high and the data bounds
        # to compute the total range
        totalmin = min(range.low, dmin)
        totalmax = max(range.high, dmax)

        # Compute the size available for the scrollbar to scroll in
        scrollrange = (totalmax - totalmin) - view
        if round(scrollrange / 20.0) > 0.0:
            ticksize = scrollrange / round(scrollrange / 20.0)
        else:
            ticksize = 1
        foo = (totalmin, totalmax, view, ticksize)

        self.trait_setq(
            range=foo,
            scroll_position=max(
                min(self.scroll_position, totalmax - view), totalmin
            ),
        )
        self._scroll_updated = True
        self.request_redraw()

    def _scroll_position_changed(self):
        super()._scroll_position_changed()

        # Notify our range that we've changed
        range = self.mapper.range
        view_width = range.high - range.low
        new_scroll_pos = self.scroll_position
        range.set_bounds(new_scroll_pos, new_scroll_pos + view_width)

    # ----------------------------------------------------------------------
    # Event listeners
    # ----------------------------------------------------------------------

    def _component_changed(self, old, new):
        # Check to see if we're currently overriding the value of self.component
        # in self.plot.  If so, then don't change the event listeners.
        if self._plot is not None:
            return
        if old is not None:
            self._modify_plot_listeners(old, "detach")
        if new is not None:
            self._modify_plot_listeners(new, "attach")
            self._update_mapper_listeners()

    def __plot_changed(self, old, new):
        if old is not None:
            self._modify_plot_listeners(old, "detach")
        elif self.component is not None:
            # Remove listeners from self.component, if it exists
            self._modify_plot_listeners(self.component, "detach")
        if new is not None:
            self._modify_plot_listeners(new, "attach")
            self._update_mapper_listeners()
        elif self.component is not None:
            self._modify_plot_listeners(self.component, "attach")
            self._update_mapper_listeners()

    def _modify_plot_listeners(self, plot, action="attach"):
        if action == "attach":
            remove = False
        else:
            remove = True
        plot.observe(
            self._component_bounds_handler, "bounds.items", remove=remove
        )
        plot.observe(
            self._component_pos_handler, "position.items", remove=remove
        )

    def _component_bounds_handler(self, event):
        self._handle_dataspace_update()
        self._widget_moved = True

    def _component_pos_handler(self, event):
        self._handle_dataspace_update()
        self._widget_moved = True

    def _update_mapper_listeners(self):
        # if self._mapper
        pass

    def _handle_mapper_updated(self):
        self._handle_dataspace_update()

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

    def _get_mapper(self):
        if self._mapper is not None:
            return self._mapper
        else:
            return getattr(self.plot, self.axis + "_mapper")

    def _set_mapper(self, new_mapper):
        self._mapper = new_mapper

    def _get_axis_index(self):
        if self._axis_index is None:
            return self._determine_axis()
        else:
            return self._axis_index

    def _set_axis_index(self, val):
        self._axis_index = val

    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _get_axis_coord(self, event, axis="index"):
        """Returns the coordinate of the event along the axis of interest
        to this tool (or along the orthogonal axis, if axis="value").
        """
        event_pos = (event.x, event.y)
        if axis == "index":
            return event_pos[self.axis_index]
        else:
            return event_pos[1 - self.axis_index]

    def _determine_axis(self):
        """Determines whether the index of the coordinate along this tool's
        axis of interest is the first or second element of an (x,y) coordinate
        tuple.

        This method is only called if self._axis_index hasn't been set (or is
        None).
        """
        if self.axis == "index":
            if self.plot.orientation == "h":
                return 0
            else:
                return 1
        else:  # self.axis == "value"
            if self.plot.orientation == "h":
                return 1
            else:
                return 0
