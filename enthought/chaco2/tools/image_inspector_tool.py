""" Defines the ImageInspectorTool, ImageInspectorOverlay, and 
ImageInspectorColorbarOverlay classes.
"""
# Enthought library imports
from enthought.enable2.api import BaseTool, KeySpec
from enthought.traits.api import Any, Bool, Enum, Event, Trait, Tuple

# Chaco imports
from enthought.chaco2.api import AbstractOverlay, ImagePlot, TextBoxOverlay


class ImageInspectorTool(BaseTool):
    """ A tool that captures the color and underlying values of an image plot.
    """

    # This event fires whenever the mouse moves over a new image point.
    # Its value is a dict with a key "color_value", and possibly a key
    # "data_value" if the plot is a color-mapped image plot.
    new_value = Event

    # Indicates whether overlays listening to this tool should be visible.
    visible = Bool(True)

    # Stores the last mouse position.  This can be used by overlays to
    # position themselves around the mouse.
    last_mouse_position = Tuple

    # This key will show and hide any ImageInspectorOverlays associated
    # with this tool.
    inspector_key = KeySpec('p')
   
    # Stores the value of self.visible when the mouse leaves the tool,
    # so that it can be restored when the mouse enters again.
    _old_visible = Trait(None, Bool(True))

    def normal_key_pressed(self, event):
        if self.inspector_key.match(event):
            self.visible = not self.visible

    def normal_mouse_leave(self, event):
        self._old_visible = self.visible
        self.visible = False

    def normal_mouse_enter(self, event):
        if self._old_visible is not None:
            self.visible = self._old_visible

    def normal_mouse_move(self, event):
        """ Handles the mouse being moved.
        
        Fires the **new_value** event with the data (if any) from the event's 
        position.
        """
        plot = self.component
        if plot is not None:
            if isinstance(plot, ImagePlot):
                ndx = plot.map_index((event.x, event.y))
                if ndx == (None, None):
                    self.new_value = None
                    return

                x_index, y_index = ndx
                image_data = plot.value
                if hasattr(plot, "_cached_mapped_image") and \
                       plot._cached_mapped_image is not None:
                    self.new_value = \
                            dict(indices=ndx,
                                 data_value=image_data.data[y_index, x_index],
                                 color_value=plot._cached_mapped_image[y_index, 
                                                                       x_index])
                    
                else:
                    self.new_value = \
                        dict(indices=ndx,
                             color_value=image_data.data[y_index, x_index])
                self.last_mouse_position = (event.x, event.y)
        return
    

class ImageInspectorOverlay(TextBoxOverlay):
    """ An overlay that displays a box containing values from an 
    ImageInspectorTool instance.
    """
    # An instance of ImageInspectorTool; this overlay listens to the tool
    # for changes, and updates its displayed text accordingly.
    image_inspector = Any

    # Anchor the text to the mouse?  (If False, then the text is in one of the
    # corners.)  Use the **align** trait to determine which corner.
    tooltip_mode = Bool(False)

    # The default state of the overlay is invisible (overrides PlotComponent).
    visible = False

    # Whether the overlay should auto-hide and auto-show based on the
    # tool's location, or whether it should be forced to be hidden or visible.
    visibility = Enum("auto", True, False)

    def _image_inspector_changed(self, old, new):
        if old:
            old.on_trait_event(self._new_value_updated, 'new_value', remove=True)
            old.on_trait_change(self._tool_visible_changed, "visible", remove=True)
        if new:
            new.on_trait_event(self._new_value_updated, 'new_value')
            new.on_trait_change(self._tool_visible_changed, "visible") 
            self._tool_visible_changed()
        
    def _new_value_updated(self, event):
        if event is None:
            self.text = ""
            if self.visibility == "auto":
                self.visible = False
            return
        elif self.visibility == "auto":
            self.visible = True

        if self.tooltip_mode:
            self.alternate_position = self.image_inspector.last_mouse_position
        else:
            self.alternate_position = None
        
        d = event
        newstring = ""
        if 'indices' in d:
            newstring += '(%d, %d)' % d['indices'] + '\n'
        if 'color_value' in d:
            newstring += "(%d, %d, %d)" % tuple(map(int,d['color_value'][:3])) + "\n"
        if 'data_value' in d:
            newstring += str(d['data_value'])

        self.text = newstring
        self.component.request_redraw()

    def _visible_changed(self):
        self.component.request_redraw()

    def _tool_visible_changed(self):
        self.visibility = self.image_inspector.visible
        if self.visibility != "auto":
            self.visible = self.visibility
    

class ImageInspectorColorbarOverlay(AbstractOverlay):
    pass
