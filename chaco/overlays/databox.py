from traits.api import Bool, Enum, Float, Int, CList, Property, Trait, observe
from enable.api import ColorTrait
from chaco.abstract_overlay import AbstractOverlay


class DataBox(AbstractOverlay):
    """
    An overlay that is a box defined by data space coordinates.  This can be
    used as a base class for various kinds of zoom boxes.  Unlike the
    "momentary" zoom box drawn for the ZoomTool, a ZoomBox is a more permanent
    visual component.
    """

    data_position = Property
    data_bounds = Property

    # Should the zoom box stay attached to the image or to the screen if the
    # component moves underneath it?
    # TODO: This basically works, but the problem is that it responds to both
    # changes in X and Y independently.  The DataRange2D needs to be updated
    # to reflect changes from its two DataRange1Ds.  The PanTool and ZoomTool
    # need to be improved that they change both dimensions at once.
    affinity = Enum("image", "screen")

    # -------------------------------------------------------------------------
    # Appearance properties (for Box mode)
    # -------------------------------------------------------------------------

    # The color of the selection box.
    color = ColorTrait("lightskyblue")

    # The alpha value to apply to **color** when filling in the selection
    # region.  Because it is almost certainly useless to have an opaque zoom
    # rectangle, but it's also extremely useful to be able to use the normal
    # named colors from Enable, this attribute allows the specification of a
    # separate alpha value that replaces the alpha value of **color** at draw
    # time.
    alpha = Trait(0.3, None, Float)

    # The color of the outside selection rectangle.
    border_color = ColorTrait("dodgerblue")

    # The thickness of selection rectangle border.
    border_size = Int(1)

    # -------------------------------------------------------------------------
    # Private Traits
    # -------------------------------------------------------------------------

    _data_position = CList([0, 0])
    _data_bounds = CList([0, 0])
    _position_valid = False
    _bounds_valid = False

    # Are we in the middle of an event handler or a property setter
    _updating = Bool(False)

    def __init__(self, *args, **kw):
        super(DataBox, self).__init__(*args, **kw)
        if hasattr(self.component, "range2d"):
            self.component.range2d._xrange.observe(
                self.my_component_moved, "updated"
            )
            self.component.range2d._yrange.observe(
                self.my_component_moved, "updated"
            )
        elif hasattr(self.component, "x_mapper") and hasattr(
            self.component, "y_mapper"
        ):
            self.component.x_mapper.range.observe(
                self.my_component_moved, "updated"
            )
            self.component.y_mapper.range.observe(
                self.my_component_moved, "updated"
            )
        else:
            raise RuntimeError(
                "DataBox cannot find a suitable mapper on its component."
            )
        self.component.observe(self.my_component_resized, "bounds.items")

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        if not self._position_valid:
            tmp = self.component.map_screen([self._data_position])
            if len(tmp.shape) == 2:
                tmp = tmp[0]
            self._updating = True
            self.position = tmp
            self._updating = False
            self._position_valid = True

        if not self._bounds_valid:
            data_x2 = self._data_position[0] + self._data_bounds[0]
            data_y2 = self._data_position[1] + self._data_bounds[1]
            tmp = self.component.map_screen((data_x2, data_y2))
            if len(tmp.shape) == 2:
                tmp = tmp[0]
            x2, y2 = tmp
            x, y = self.position
            self._updating = True
            self.bounds = [x2 - x, y2 - y]
            self._updating = False
            self._bounds_valid = True

        with gc:
            gc.set_antialias(0)
            gc.set_line_width(self.border_size)
            gc.set_stroke_color(self.border_color_)
            gc.clip_to_rect(
                component.x, component.y, component.width, component.height
            )
            rect = self.position + self.bounds

            if self.color != "transparent":
                if self.alpha:
                    color = list(self.color_)
                    if len(color) == 4:
                        color[3] = self.alpha
                    else:
                        color += [self.alpha]
                else:
                    color = self.color_
                gc.set_fill_color(color)
                gc.rect(*rect)
                gc.draw_path()
            else:
                gc.rect(*rect)
                gc.stroke_path()

    # -------------------------------------------------------------------------
    # Property setters/getters, event handlers
    # -------------------------------------------------------------------------

    def _get_data_position(self):
        return self._data_position

    def _set_data_position(self, val):
        self._data_position = val
        self._position_valid = False
        self.trait_property_changed("data_position", self._data_position)

    def _get_data_bounds(self):
        return self._data_bounds

    def _set_data_bounds(self, val):
        self._data_bounds = val
        self._bounds_valid = False
        self.trait_property_changed("data_bounds", self._data_bounds)

    @observe("position.items")
    def _update_position(self, event=None):
        if self._updating:
            return
        tmp = self.component.map_data(self.position)
        if tmp.ndim == 2:
            tmp = tmp[0]
        self._data_position = tmp
        self.trait_property_changed("data_position", self._data_position)

    @observe("bounds.items")
    def _update_bounds(self, event=None):
        if self._updating:
            return
        data_x2, data_y2 = self.component.map_data((self.x2, self.y2))
        data_pos = self._data_position
        self._data_bounds = [data_x2 - data_pos[0], data_y2 - data_pos[1]]
        self.trait_property_changed("data_bounds", self._data_bounds)

    def my_component_moved(self, event=None):
        if self.affinity == "screen":
            # If we have screen affinity, then we need to take our current position
            # and map that back down into data coords
            self._update_position()
            self._update_bounds()
        self._bounds_valid = False
        self._position_valid = False

    def my_component_resized(self, event=None):
        self._bounds_valid = False
        self._position_valid = False
