
# Enthought library imports
from enthought.traits.api import Any, Bool, Event, Tuple

# Chaco imports
from enthought.chaco2.api import AbstractOverlay, BaseTool, ImagePlot, TextBoxOverlay


class ImageInspectorTool(BaseTool):
    """ Tool that reads out the color and underlying values of an image plot """

    # This event fires whenever the mouse moves over a new image point.
    # Its value is a dict with a key "color_value", and possibly a key
    # "data_value" if the plot is a colormapped image plot.
    new_value = Event

    # Stores the last mouse position.  This can be used by overlays to
    # position themselves around the mouse.
    last_mouse_position = Tuple

    def normal_mouse_move(self, event):
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
                    self.new_value = dict(data_value = image_data.data[y_index, x_index],
                                          color_value = plot._cached_mapped_image[y_index, x_index])
                    
                else:
                    self.new_value = dict(color_value = image_data.data[y_index, x_index])
                self.last_mouse_position = (event.x, event.y)
        return
    

class ImageInspectorOverlay(TextBoxOverlay):

    # An instance of the ImageInspectorTool; this overlay listens to the tool
    # for changes, and updates its displayed text accordingly.
    image_inspector = Any

    # Should the text be anchored to the mouse?  (If false, then the
    # text is in one of the corners.)  Use the 'align' trait to determine
    # which corner.
    tooltip_mode = Bool(False)

    # Make the default state of the overlay invisible
    visible = False

    def _image_inspector_changed(self, old, new):
        if old:
            old.on_trait_event(self._new_value_updated, 'new_value', remove=True)
        if new:
            new.on_trait_event(self._new_value_updated, 'new_value')
        
    def _new_value_updated(self, event):
        if event is None:
            self.text = ""
            self.visible = False
            self.component.request_redraw()
            return
        else:
            self.visible = True

        if self.tooltip_mode:
            self.alternate_position = self.image_inspector.last_mouse_position
        else:
            self.alternate_position = None
        
        d = event
        newstring = ""
        if 'color_value' in d:
            newstring += "(%d, %d, %d)" % tuple(map(int,d['color_value'][:3])) + "\n"
        if 'data_value' in d:
            newstring += str(d['data_value'])

        self.text = newstring
        self.component.request_redraw()
    

class ImageInspectorColorbarOverlay(AbstractOverlay):
    pass
