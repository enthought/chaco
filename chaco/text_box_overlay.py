""" Defines the TextBoxOverlay class.
"""
from __future__ import with_statement

# Enthought library imports
from enable.api import ColorTrait
from kiva.trait_defs.kiva_font_trait import KivaFont
from traits.api import Any, Enum, Int, Str, Float, Trait, Bool

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

    # The alpha value to apply to **bgcolor**
    alpha = Trait(1.0, None, Float)

    # The color of the outside box.
    border_color = ColorTrait("dodgerblue")

    # The color of the text.
    text_color = ColorTrait("black")

    # The thickness of box border.
    border_size = Int(1)
    
    # The border visibility. Defaults to true to duplicate previous behavior.
    border_visible = Bool(True)

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

        # draw the label on a transparent box. This allows us to draw
        # different shapes and put the text inside it without the label
        # filling a rectangle on top of it
        label = Label(text=self.text, font=self.font, bgcolor="transparent",
                      color=self.text_color, margin=5)
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

        # attempt to get the box entirely within the component
        x_min, y_min, x_max, y_max = (component.x,
                                      component.y,
                                      component.x + component.width,
                                      component.y + component.height)
        if x + width > x_max:
            x = max(x_min, x_max - width)
        if y + height > y_max:
            y = max(y_min, y_max - height)
        elif y < y_min:
            y = y_min

        # apply the alpha channel
        color = self.bgcolor_
        if self.bgcolor != "transparent":
            if self.alpha:
                color = list(self.bgcolor_)
                if len(color) == 4:
                    color[3] = self.alpha
                else:
                    color += [self.alpha]

        with gc:
            gc.translate_ctm(x, y)

            gc.set_line_width(self.border_size)
            gc.set_stroke_color(self.border_color_)
            gc.set_fill_color(color)

            if self.border_visible:
                # draw a rounded rectangle.
                x = y = 0
                end_radius = 8.0
                gc.begin_path()
                gc.move_to(x + end_radius, y)
                gc.arc_to(x + width, y,
                        x + width,
                        y + end_radius, end_radius)
                gc.arc_to(x + width,
                        y + height,
                        x + width - end_radius,
                        y + height, end_radius)
                gc.arc_to(x, y + height,
                        x, y,
                        end_radius)
                gc.arc_to(x, y,
                        x + width + end_radius,
                        y, end_radius)
                gc.draw_path()

            label.draw(gc)
