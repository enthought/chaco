""" Defines the PlotLabel class.
"""
from enthought.kiva import font_metrics_provider
from enthought.traits.api import DelegatesTo, Enum, Instance, Str, Trait

from abstract_overlay import AbstractOverlay
from label import Label


LabelDelegate = DelegatesTo("_label")

class PlotLabel(AbstractOverlay):
    """ A label used by plots. 
    
    This class wraps a simple Label instance, and delegates some traits to it.
    """
    
    # The text of the label.
    text = LabelDelegate
    # The color of the label text.
    color = DelegatesTo("_label")
    # The font for the label text.
    font = LabelDelegate
    # The angle of rotation of the label.
    angle = DelegatesTo("_label", "rotate_angle")

    bgcolor = LabelDelegate
    border_width = LabelDelegate
    border_color = LabelDelegate
    border_visible = LabelDelegate
    margin = LabelDelegate
    line_spacing = LabelDelegate

    #------------------------------------------------------------------------
    # Layout-related traits
    #------------------------------------------------------------------------
    
    # Horizontal justification used if the label has more horizontal space
    # than it needs.
    hjustify = Enum("center", "left", "right")
    
    # Vertical justification used if the label has more vertical space than it
    # needs.
    vjustify = Enum("center", "bottom", "top")
    
    # The position of this label relative to the object it is overlaying.
    # Can be "top", "left", "right", "bottom", and optionally can be preceeded
    # by the words "inside" or "outside", separated by a space.  If "inside"
    # and "outside" are not provided, then defaults to "outside".
    # Examples:
    #     inside top
    #     outside right
    overlay_position = Trait("outside top", Str, None)
    
    # Should this PlotLabel modify the padding on its underlying component
    # if there is not enough room to lay out the text?
    # FIXME: This could cause cycles in layout, so not implemented for now
    #modify_component = Bool(True)

    # By default, this acts like a component and will render on the main
    # "plot" layer unless its **component** attribute gets set.
    draw_layer = "plot"

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # The label has a fixed height and can be resized horizontally. (Overrides
    # PlotComponent.)
    resizable = "h"

    # The Label instance this plot label is wrapping.
    _label = Instance(Label, args=())

    
    def __init__(self, text="", *args, **kw):
        super(PlotLabel, self).__init__(*args, **kw)
        self.text = text
        return
    
    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws this label overlaid on another component.
        
        Overrides AbstractOverlay.
        """
        self._draw_overlay(gc, view_bounds, mode)
        return

    def get_preferred_size(self):
        """ Returns the label's preferred size.
        
        Overrides PlotComponent.
        """
        dummy_gc = font_metrics_provider()
        size = self._label.get_bounding_box(dummy_gc)
        return size
    
    def do_layout(self):
        """ Tells this component to do layout.
        
        Overrides PlotComponent.
        """
        if self.component is not None:
            self._layout_as_overlay()
        else:
            self._layout_as_component()
        return
    
    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        """ Draws the overlay layer of a component.
        
        Overrides PlotComponent.
        """
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
            
            # XXX: Uncomment this after we fix kiva GL backend's clip stack
            #gc.clip_to_rect(self.x, self.y, self.width, self.height)

            # We have to translate to our position because the label
            # tries to draw at (0,0).
            gc.translate_ctm(self.x + x_offset, self.y + y_offset)
            self._label.draw(gc)
        finally:
            gc.restore_state()
        return
    
    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        if self.component is None:
            # We are not overlaying anything else, so we should render
            # on this layer
            self._draw_overlay(gc, view_bounds, mode)

    def _layout_as_component(self, size=None, force=False):
        pass
    
    def _layout_as_overlay(self, size=None, force=False):
        """ Lays out the label as an overlay on another component.
        """
        if self.component is not None:
            orientation = self.overlay_position
            outside = True
            if "inside" in orientation:
                tmp = orientation.split()
                tmp.remove("inside")
                orientation = tmp[0]
                outside = False
            elif "outside" in orientation:
                tmp = orientation.split()
                tmp.remove("outside")
                orientation = tmp[0]

            if orientation in ("left", "right"):
                self.y = self.component.y
                self.height = self.component.height
                if not outside:
                    gc = font_metrics_provider()
                    self.width = self._label.get_bounding_box(gc)[0]
                if orientation == "left":
                    if outside:
                        self.x = self.component.outer_x
                        self.width = self.component.padding_left
                    else:
                        self.outer_x = self.component.x
                elif orientation == "right":
                    if outside:
                        self.x = self.component.x2 + 1
                        self.width = self.component.padding_right
                    else:
                        self.x = self.component.x2 - self.outer_width
            elif orientation in ("bottom", "top"):
                self.x = self.component.x
                self.width = self.component.width
                if not outside:
                    gc = font_metrics_provider()
                    self.height = self._label.get_bounding_box(gc)[1]
                if orientation == "bottom":
                    if outside:
                        self.y = self.component.outer_y
                        self.height = self.component.padding_bottom
                    else:
                        self.outer_y = self.component.y
                elif orientation == "top":
                    if outside:
                        self.y = self.component.y2 + 1
                        self.height = self.component.padding_top
                    else:
                        self.y = self.component.y2 - self.outer_height
            else:
                # Leave the position alone
                pass
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

    def _overlay_position_changed(self):
        self.do_layout()

    def _component_changed(self, old, new):
        if new:
            self.draw_layer = "overlay"
        else:
            self.draw_layer = "plot"
        return



# EOF
