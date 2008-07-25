""" Defines the TextBoxOverlay class.
"""
# Enthought library imports
from enthought.enable.api import ColorTrait
from enthought.kiva.traits.kiva_font_trait import KivaFont
from enthought.traits.api import Any, Enum, Int, Str

# Local, relative imports
from abstract_overlay import AbstractOverlay
from label import Label


class TextBoxOverlay(AbstractOverlay):
    """ Draws a box with text in it.
    """

    #### Configuration traits ##################################################

    # The text to display in the box.
    text = Str
    # The font to use for the text.
    font = KivaFont("modern 12")
    # The background color for the box (overrides AbstractOverlay).
    bgcolor = ColorTrait("transparent")
    # Number of pixels of padding around the text within the box.
    padding = Int(5)
    # Alignment of the text in the box:
    #
    # * "ur": upper right
    # * "ul": upper left
    # * "ll": lower left
    # * "lr": lower right
    align = Enum("ur", "ul", "ll", "lr")

    # This allows subclasses to specify an alternate position for the root
    # of the text box.  Must be a sequence of length 2.
    alternate_position = Any

    #### Public 'AbstractOverlay' interface ####################################

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws the box overlaid on another component.
        
        Overrides AbstractOverlay.
        """

        if not self.visible:
            return

        label = Label(text=self.text, font=self.font, bgcolor=self.bgcolor,
                      margin=5)
        width, height = label.get_width_height(gc)
        valign, halign = self.align

        if self.alternate_position:
            x, y = self.alternate_position
            if valign == "u":
                y += self.padding
            else:
                y -= self.padding + height

            if halign == "r":
                x += self.padding
            else:
                x -= self.padding + width
        else:
            if valign == "u":
                y = component.y2 - self.padding - height
            else:
                y = component.y + self.padding

            if halign == "r":
                x = component.x2 - self.padding - width
            else:
                x = component.x + self.padding

        gc.save_state()
        gc.translate_ctm(x, y)
        label.draw(gc)
        gc.restore_state()
