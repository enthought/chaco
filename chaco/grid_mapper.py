"""
Defines the GridMapper class, which maps from a 2-D region in data space
into a structured (gridded) 1-D output space.
"""

# Python standard library imports
from contextlib import contextmanager

# Major library imports
from numpy import empty, transpose

# Enthought library imports
from traits.api import Bool, DelegatesTo, Instance, Float, Property

# Local relative imports
from abstract_mapper import AbstractMapper
from base_1d_mapper import Base1DMapper
from data_range_2d import DataRange2D
from linear_mapper import LinearMapper
from log_mapper import LogMapper


class GridMapper(AbstractMapper):
    """
    Maps a 2-D data space to and from screen space by specifying a 2-tuple in
    data space or by specifying a pair of screen coordinates.

    The mapper concerns itself only with metric and not with orientation. So,
    to "flip" a screen space orientation, swap the appropriate screen space
    values for **x_low_pos**, **x_high_pos**, **y_low_pos**, and
    **y_high_pos**.
    """

    # The data-space bounds of the mapper.
    range = Instance(DataRange2D)

    # The screen space position of the lower bound of the horizontal axis.
    x_low_pos = Float(0.0)

    # The screen space position of the upper bound of the horizontal axis.
    x_high_pos = Float(1.0)

    # The screen space position of the lower bound of the vertical axis.
    y_low_pos = Float(0.0)

    # The screen space position of the upper bound of the vertical axis.
    y_high_pos = Float(1.0)

    # Convenience property for low and high positions in one structure.
    # Must be a tuple (x_low_pos, x_high_pos, y_low_pos, y_high_pos).
    screen_bounds = Property

    # Should the mapper stretch the dataspace when its screen space bounds are
    # modified (default), or should it preserve the screen-to-data ratio and
    # resize the data bounds?  If the latter, it will only try to preserve
    # the ratio if both screen and data space extents are non-zero.
    stretch_data_x = DelegatesTo("_xmapper", prefix="stretch_data")
    stretch_data_y = DelegatesTo("_ymapper", prefix="stretch_data")

    # Should the mapper try to maintain a fixed aspect ratio between x and y
    maintain_aspect_ratio = Bool

    # The aspect ratio that we wish to maintain
    aspect_ratio = Float(1.0)

    #------------------------------------------------------------------------
    # Private Traits
    #------------------------------------------------------------------------

    _updating_submappers = Bool(False)
    _updating_aspect = Bool(False)

    _xmapper = Instance(Base1DMapper)
    _ymapper = Instance(Base1DMapper)

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, x_type="linear", y_type="linear", range=None, **kwargs):
        # TODO: This is currently an implicit assumption, i.e. that the range
        # will be passed in to the constructor.  It would be impossible to
        # create the xmapper and ymapper otherwise.  However, this should be
        # changed so that the mappers get created or modified in response to
        # the .range attribute changing, instead of requiring the range to
        # be passed in at construction time.
        self.range = range

        if "_xmapper" not in kwargs:
            if x_type == "linear":
                self._xmapper = LinearMapper(range=self.range.x_range)
            elif x_type == "log":
                self._xmapper = LogMapper(range=self.range.x_range)
            else:
                raise ValueError("Invalid x axis type: %s" % x_type)
        else:
            self._xmapper = kwargs.pop("_xmapper")

        if "_ymapper" not in kwargs:
            if y_type == "linear":
                self._ymapper = LinearMapper(range=self.range.y_range)
            elif y_type == "log":
                self._ymapper = LogMapper(range=self.range.y_range)
            else:
                raise ValueError("Invalid y axis type: %s" % y_type)
        else:
            self._ymapper = kwargs.pop("_ymapper")

        # Now that the mappers are created, we can go to the normal HasTraits
        # constructor, which might set values that depend on us having a valid
        # range and mappers.
        super(GridMapper, self).__init__(**kwargs)

    def map_screen(self, data_pts):
        """ map_screen(data_pts) -> screen_array

        Maps values from data space into screen space.
        """
        xs, ys = transpose(data_pts)
        screen_xs = self._xmapper.map_screen(xs)
        screen_ys = self._ymapper.map_screen(ys)
        screen_pts = empty(shape=xs.shape+(2,), dtype=float)
        screen_pts[..., 0] = screen_xs
        screen_pts[..., 1] = screen_ys
        return screen_pts

    def map_data(self, screen_pts):
        """ map_data(screen_pts) -> data_vals

        Maps values from screen space into data space.
        """
        screen_xs, screen_ys = transpose(screen_pts)
        xs = self._xmapper.map_data(screen_xs)
        ys = self._ymapper.map_data(screen_ys)
        data_pts = empty(shape=xs.shape+(2,), dtype=float)
        data_pts[..., 0] = xs
        data_pts[..., 1] = ys
        return data_pts

    def map_data_array(self, screen_pts):
        return self.map_data(screen_pts)

    #------------------------------------------------------------------------
    # Private Methods
    #------------------------------------------------------------------------

    def _update_bounds(self):
        with self._update_submappers():
            self._xmapper.screen_bounds = (self.x_low_pos, self.x_high_pos)
            self._ymapper.screen_bounds = (self.y_low_pos, self.y_high_pos)
        self.updated = True

    def _update_range(self):
        self.updated = True

    def _update_aspect_x(self):
        y_width = self._ymapper.high_pos - self._ymapper.low_pos
        if y_width == 0:
            return
        y_scale = (self._ymapper.range.high - self._ymapper.range.low)/y_width
        x_range_low = self._xmapper.range.low
        x_width = self._xmapper.high_pos - self._xmapper.low_pos
        sign = self._xmapper.sign * self._ymapper.sign
        if x_width == 0 or sign == 0:
            return
        x_scale = sign*y_scale/self.aspect_ratio
        with self._update_aspect():
            self._xmapper.range.set_bounds(x_range_low, x_range_low +
                x_scale*x_width)

    def _update_aspect_y(self):
        x_width = self._xmapper.high_pos - self._xmapper.low_pos
        if x_width == 0:
            return
        x_scale = (self._xmapper.range.high - self._xmapper.range.low)/x_width
        y_range_low = self._ymapper.range.low
        y_width = self._ymapper.high_pos-self._ymapper.low_pos
        sign = self._xmapper.sign * self._ymapper.sign
        if y_width == 0 or sign == 0:
            return
        y_scale = sign*x_scale*self.aspect_ratio
        with self._update_aspect():
            self._ymapper.range.set_bounds(y_range_low, y_range_low +
                y_scale*y_width)

    #------------------------------------------------------------------------
    # Property handlers
    #------------------------------------------------------------------------

    def _range_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._update_range, "updated", remove=True)
        if new is not None:
            new.on_trait_change(self._update_range, "updated")
            if self._xmapper is not None:
                self._xmapper.range = new.x_range
            if self._ymapper is not None:
                self._ymapper.range = new.y_range
            self._update_range()

    def _x_low_pos_changed(self):
        self._xmapper.low_pos = self.x_low_pos

    def _x_high_pos_changed(self):
        self._xmapper.high_pos = self.x_high_pos

    def _y_low_pos_changed(self):
        self._ymapper.low_pos = self.y_low_pos

    def _y_high_pos_changed(self):
        self._ymapper.high_pos = self.y_high_pos

    def _set_screen_bounds(self, new_bounds):
        # TODO: figure out a way to not need to do this check:
        if self.screen_bounds == new_bounds:
            return
        self.set(x_low_pos=new_bounds[0], trait_change_notify=False)
        self.set(x_high_pos=new_bounds[1], trait_change_notify=False)
        self.set(y_low_pos=new_bounds[2], trait_change_notify=False)
        self.set(y_high_pos=new_bounds[3], trait_change_notify=False)
        self._update_bounds()

    def _get_screen_bounds(self):
        return (self.x_low_pos, self.x_high_pos,
                self.y_low_pos, self.y_high_pos)

    def _updated_fired_for__xmapper(self):
        if not self._updating_aspect:
            if self.maintain_aspect_ratio and self.stretch_data_x:
                self._update_aspect_y()
        if not self._updating_submappers:
            self.updated = True

    def _updated_fired_for__ymapper(self):
        if not self._updating_aspect:
            if self.maintain_aspect_ratio and self.stretch_data_y:
                self._update_aspect_x()
        if not self._updating_submappers:
            self.updated = True

    @contextmanager
    def _update_submappers(self):
        self._updating_submappers = True
        try:
            yield
        finally:
            self._updating_submappers = False

    @contextmanager
    def _update_aspect(self):
        self._updating_aspect = True
        try:
            yield
        finally:
            self._updating_aspect = False
