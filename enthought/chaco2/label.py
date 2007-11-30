""" Defines the Label class.
"""
# Major library imports
from math import pi

# Enthought library imports
from enthought.enable2.api import black_color_trait, transparent_color_trait
from enthought.kiva.traits.kiva_font_trait import KivaFont
from enthought.traits.api import Any, false, Float, HasTraits, Int, \
                                 List, Str, Instance


class Label(HasTraits):
    """ A label used by overlays.
    """

    # The label text.  Carriage returns (\n) are always connverted into
    # line breaks.
    text = Str

    # The angle of rotation of the label.  Only multiples of 90 are supported.
    rotate_angle = Float(0)

    # The color of the label text.
    color = black_color_trait

    # The background color of the label.
    bgcolor = transparent_color_trait

    # The width of the label border. If it is 0, then it is not shown.
    border_width = Int(0)

    # The color of the border.
    border_color = black_color_trait

    # The font of the label text.
    font = KivaFont("modern 10")

    # Number of pixels of margin around the label, for both X and Y dimensions.
    margin = Int(2)

    # Number of pixels of spacing between lines of text.
    line_spacing = Int(5)


    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    _bounding_box = List()
    _position_cache_valid = false


    def __init__(self, **traits):
        HasTraits.__init__(self, **traits)
        self._bounding_box = [0,0]
        return

    def _calc_line_positions(self, gc):
        if not self._position_cache_valid:
            gc.save_state()
            gc.set_font(self.font)
            # The bottommost line starts at postion (0,0).
            x_pos = []
            y_pos = []
            self._bounding_box = [0,0]
            margin = self.margin
            prev_y_pos = margin
            prev_y_height = -self.line_spacing
            max_width = 0
            for line in self.text.split("\n")[::-1]:
                if line != "":
                    (width, height, descent, leading) = gc.get_full_text_extent(line)
                    if width > max_width:
                        max_width = width
                    new_y_pos = prev_y_pos + prev_y_height - descent + self.line_spacing
                else:
                    # For blank lines, we use the height of the previous line, if there
                    # is one.  The width is 0.
                    leading = 0
                    if prev_y_height != -self.line_spacing:
                        new_y_pos = prev_y_pos + prev_y_height + self.line_spacing
                        height = prev_y_height
                    else:
                        new_y_pos = prev_y_pos
                        height = 0
                x_pos.append(-leading + margin)
                y_pos.append(new_y_pos)
                prev_y_pos = new_y_pos
                prev_y_height = height
            gc.restore_state()

            self._line_xpos = x_pos[::-1]
            self._line_ypos = y_pos[::-1]
            self._bounding_box[0] = max_width + 2*margin + 2*self.border_width
            self._bounding_box[1] = prev_y_pos + prev_y_height + margin + 2*self.border_width
            self._position_cache_valid = True
        return

    def get_width_height(self, gc):
        """ Returns the width and height of the label, in the rotated frame of 
        reference.
        """
        self._calc_line_positions(gc)
        width, height = self._bounding_box
        return width, height

    def get_bounding_box(self, gc):
        """ Returns a rectangular bounding box for the Label as (width,height).
        """
        # FIXME: Need to deal with non 90 deg rotations
        width, height = self.get_width_height(gc)
        if self.rotate_angle in (90.0, 270.0):
            return (height, width)
        elif self.rotate_angle in (0.0, 180.0):
            return (width, height)
        else:
            angle = self.rotate_angle
            return (abs(width*cos(angle))+abs(height*sin(angle)), 
                    abs(height*sin(angle))+abs(width*cos(angle)))

    def get_bounding_poly(self, gc):
        """
        Returns a list [(x0,y0), (x1,y1),...] of tuples representing a polygon
        that bounds the label.
        """
        raise NotImplementedError

    def draw(self, gc):
        """ Draws the label.

        This method assumes the graphics context has been translated to the
        correct position such that the origin is at the lower left-hand corner
        of this text label's box.
        """
        # For this version we're not supporting rotated text.
        # temp modified for only one line
        self._calc_line_positions(gc)
        try:
            gc.save_state()

            # Draw border and fill background
            width, height = self._bounding_box
            if self.bgcolor != "transparent":
                gc.set_fill_color(self.bgcolor_)
                gc.rect(0, 0, width, height)
                gc.fill_path()
            if self.border_width > 0:
                gc.set_stroke_color(self.border_color_)
                gc.set_line_width(self.border_width)
                border_offset = (self.border_width-1)/2.0
                gc.rect(border_offset, border_offset, width-2*border_offset, height-2*border_offset)
                gc.stroke_path()

            gc.set_fill_color(self.color_)
            gc.set_stroke_color(self.color_)
            gc.set_font(self.font)
            if self.font.size<=8.0:
                gc.set_antialias(0)
            else:
                gc.set_antialias(1)

            gc.rotate_ctm(pi/180.0*self.rotate_angle)

            #margin = self.margin
            lines = self.text.split("\n")
            gc.translate_ctm(self.border_width, self.border_width)
            width, height = self.get_width_height(gc)

            for i, line in enumerate(lines):
                if line == "":
                    continue

                if self.rotate_angle==90. or self.rotate_angle==270.:
                    x_offset = round(self._line_ypos[i])
                    # this should really be "... - height/2" but
                    # that looks wrong
                    y_offset = round(self._line_xpos[i] - height)
                else:
                    x_offset = round(self._line_xpos[i])
                    y_offset = round(self._line_ypos[i])
                gc.set_text_position(0,0)
                gc.translate_ctm(x_offset, y_offset)

                gc.show_text(line)
                gc.translate_ctm(-x_offset, -y_offset)
        finally:
            gc.restore_state()
        return

    def _font_changed(self):
        self._position_cache_valid = False

    def _margin_changed(self):
        self._position_cache_valid = False

    def _text_changed(self):
        self._position_cache_valid = False

    def _rotate_angle_changed(self):
        self._position_cache_valid = False

