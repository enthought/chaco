
from enthought.kiva import font_metrics_provider
from enthought.traits.api import Delegate, Enum, Instance

from abstract_overlay import AbstractOverlay
from label import Label


class PlotLabel(AbstractOverlay):
    
    text = Delegate("_label")
    color = Delegate("_label", modify=True)
    font = Delegate("_label")
    angle = Delegate("_label", "rotate_angle")
    
    #------------------------------------------------------------------------
    # Layout-related traits
    #------------------------------------------------------------------------
    
    # Horizontal justification for when we are given more horizontal space
    # than we need
    hjustify = Enum("center", "left", "right")
    
    # Vertical justification for when we are given more vertical space than
    # we need
    vjustify = Enum("center", "bottom", "top")
    
    # The position of this label relative to the object it is overlaying
    overlay_position = Enum("top", "bottom", "left", "right")
    
    # Should this PlotLabel modify the padding on its underlying component
    # if there is not enough room to lay out the text?
    # FIXME: This could cause cycles in layout, so not implemented for now
    #modify_component = true

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # Override the value inherited from PlotComponent.  Text labels have a 
    # fixed height
    resizable = "h"

    # The Label instance we are wrapping
    _label = Instance(Label, args=())

    
    def __init__(self, text="", *args, **kw):
        super(PlotLabel, self).__init__(*args, **kw)
        self.text = text
        return
    
    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        self._draw_overlay(gc, view_bounds, mode)
        return
    
    def get_preferred_size(self):
        dummy_gc = font_metrics_provider()
        size = self._label.get_bounding_box(dummy_gc)
        return size
    
    def do_layout(self):
        if self.component is not None:
            self._layout_as_overlay()
        else:
            super(AbstractOverlay, self).do_layout()
        return
    
    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        try:
            # Perform justification and compute the correct offsets for
            # the label position
            width, height = self._label.get_bounding_box(gc)
            if self.hjustify == "left":
                x_offset = 0
            elif self.hjustify == "right":
                x_offset = self.width - width
            elif self.hjustify == "center":
                x_offset = int((self.width - width) / 2)
            
            if self.vjustify == "bottom":
                y_offset = 0
            elif self.vjustify == "top":
                y_offset = self.height - height
            elif self.vjustify == "center":
                y_offset = int((self.height - height) / 2)
            
            gc.save_state()
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            # We have to translate to our position because the label
            # tries to draw at (0,0)
            gc.translate_ctm(self.x + x_offset, self.y + y_offset)
            self._label.draw(gc)
        finally:
            gc.restore_state()
        return
    
    def _layout_as_overlay(self, size=None, force=False):
        if self.component is not None:
            orientation = self.overlay_position
            if orientation in ("left", "right"):
                self.y = self.component.y
                self.height = self.component.height
                if orientation == "left":
                    self.width = self.component.padding_left
                    self.x = self.component.outer_x
                elif orientation == "right":
                    self.width = self.component.padding_right
                    self.x = self.component.x2 + 1
            else:
                self.x = self.component.x
                self.width = self.component.width
                if orientation == "bottom":
                    self.height = self.component.padding_bottom
                    self.y = self.component.outer_y
                elif orientation == "top":
                    self.height = self.component.padding_top
                    self.y = self.component.y2 + 1
        return

    def _text_changed(self, old, new):
        self._label.text = new
        self.do_layout()
        return

    def _font_changed(self, old, new):
        self._label.font = new
        self.do_layout()
        return

    def _angle_changed(self, old, new):
        self._label.rotate_angle = new
        self.do_layout()
        return

    def _component_changed(self, old, new):
        if new:
            self.draw_layer = "overlay"
        else:
            self.draw_layer = "plot"
        return



# EOF
