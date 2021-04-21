""" Defines the Label class.
"""


# Major library imports
from math import cos, sin, pi
from numpy import array, dot

# Enthought library imports
from enable.api import black_color_trait, transparent_color_trait
from kiva.constants import FILL
from kiva.trait_defs.kiva_font_trait import KivaFont
from traits.api import Any, Bool, Float, HasTraits, Int, List, Str, observe


class Label(HasTraits):
    """A label used by overlays.

    Label is not a Component; it's just an object encapsulating text settings
    and appearance attributes.  It can be used by components that need text
    labels to store state, perform layout, and render the text.
    """

    # The anchor point is the position on the label that is placed at the
    # label's position.  The label is also rotated relative to this point.
    # "Left" refers to the left edge of the text's bounding box (including
    # margin), while "center" refers to the horizontal and vertical center
    # of the bounding box.
    # TODO: Implement this and test thoroughly
    # anchor = Enum("left", "right", "top", "bottom", "center",
    #              "top left", "top right", "bottom left", "bottom right")

    #: The label text.  Carriage returns (\n) are always connverted into
    #: line breaks.
    text = Str

    #: The angle of rotation of the label.
    rotate_angle = Float(0)

    #: The color of the label text.
    color = black_color_trait

    #: The background color of the label.
    bgcolor = transparent_color_trait

    #: The width of the label border. If it is 0, then it is not shown.
    border_width = Int(0)

    #: The color of the border.
    border_color = black_color_trait

    #: Whether or not the border is visible
    border_visible = Bool(True)

    #: The font of the label text.
    font = KivaFont("modern 10")

    #: Number of pixels of margin around the label, for both X and Y dimensions.
    margin = Int(2)

    #: Number of pixels of spacing between lines of text.
    line_spacing = Int(5)

    #: Number of pixels to limit the width of the label to. Lines which are
    #: too long will be broken to fit on word boundaries. Line width is
    #: calculated without considering the value of `margin`.
    #: A `max_width` of 0.0 means that lines will not be broken.
    max_width = Float(0.0)

    # ------------------------------------------------------------------------
    # Private traits
    # ------------------------------------------------------------------------

    _bounding_box = List()
    _position_cache_valid = Bool(False, transient=True)
    _text_needs_fitting = Bool(False)
    _line_xpos = Any()
    _line_ypos = Any()
    _rot_matrix = Any()

    def __init__(self, **traits):
        super().__init__(**traits)
        self._bounding_box = [0, 0]

    def get_width_height(self, gc):
        """Returns the width and height of the label, in the rotated frame of
        reference.
        """
        self._fit_text_to_max_width(gc)
        self._calc_line_positions(gc)
        width, height = self._bounding_box
        return width, height

    def get_bounding_box(self, gc):
        """Returns a rectangular bounding box for the Label as (width,height)."""
        width, height = self.get_width_height(gc)
        if self.rotate_angle in (90.0, 270.0):
            return (height, width)
        elif self.rotate_angle in (0.0, 180.0):
            return (width, height)
        else:
            angle = self.rotate_angle
            return (
                abs(width * cos(angle)) + abs(height * sin(angle)),
                abs(height * sin(angle)) + abs(width * cos(angle)),
            )

    def get_bounding_poly(self, gc):
        """Returns a list [(x0,y0), (x1,y1),...] of tuples representing a
        polygon that bounds the label.
        """
        width, height = self.get_width_height(gc)
        offset = array(self.get_bounding_box(gc)) / 2.0
        # unrotated points relative to centre
        base_points = [
            array([[-width / 2.0], [-height / 2.0]]),
            array([[-width / 2.0], [height / 2.0]]),
            array([[width / 2.0], [height / 2.0]]),
            array([[width / 2.0], [-height / 2.0]]),
            array([[-width / 2.0], [-height / 2.0]]),
        ]
        # rotate about centre, and offset to bounding box coords
        points = [
            dot(self.get_rotation_matrix(), point).transpose()[0] + offset
            for point in base_points
        ]
        return points

    def get_rotation_matrix(self):
        return array(
            [
                [cos(self.rotate_angle), -sin(self.rotate_angle)],
                [sin(self.rotate_angle), cos(self.rotate_angle)],
            ]
        )

    def draw(self, gc):
        """Draws the label.

        This method assumes the graphics context has been translated to the
        correct position such that the origin is at the lower left-hand corner
        of this text label's box.
        """
        # Make sure `max_width` is respected
        self._fit_text_to_max_width(gc)

        # For this version we're not supporting rotated text.
        self._calc_line_positions(gc)

        with gc:
            bb_width, bb_height = self.get_bounding_box(gc)

            # Rotate label about center of bounding box
            width, height = self._bounding_box
            gc.translate_ctm(bb_width / 2.0, bb_height / 2.0)
            gc.rotate_ctm(pi / 180.0 * self.rotate_angle)
            gc.translate_ctm(-width / 2.0, -height / 2.0)

            # Draw border and fill background
            if self.bgcolor != "transparent":
                gc.set_fill_color(self.bgcolor_)
                gc.draw_rect((0, 0, width, height), FILL)
            if self.border_visible and self.border_width > 0:
                gc.set_stroke_color(self.border_color_)
                gc.set_line_width(self.border_width)
                border_offset = (self.border_width - 1) / 2.0
                gc.rect(
                    border_offset,
                    border_offset,
                    width - 2 * border_offset,
                    height - 2 * border_offset,
                )
                gc.stroke_path()

            gc.set_fill_color(self.color_)
            gc.set_stroke_color(self.color_)
            gc.set_font(self.font)
            if self.font.size <= 8.0:
                gc.set_antialias(0)
            else:
                gc.set_antialias(1)

            lines = self.text.split("\n")
            if self.border_visible:
                gc.translate_ctm(self.border_width, self.border_width)
            width, height = self.get_width_height(gc)

            for i, line in enumerate(lines):
                if line == "":
                    continue
                x_offset = round(self._line_xpos[i])
                y_offset = round(self._line_ypos[i])
                gc.set_text_position(x_offset, y_offset)
                gc.show_text(line)

    # ------------------------------------------------------------------------
    # Trait handlers
    # ------------------------------------------------------------------------

    def _text_changed(self):
        self._text_needs_fitting = self.max_width > 0.0

    @observe("font,margin,text,rotate_angle")
    def _invalidate_position_cache(self, event):
        self._position_cache_valid = False

    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _fit_text_to_max_width(self, gc):
        """Break the text into lines whose width is no greater than
        `max_width`.
        """
        if self._text_needs_fitting:
            lines = []

            with gc:
                gc.set_font(self.font)
                for line in self.text.split("\n"):
                    if line == "":
                        lines.append(line)
                        continue

                    width = gc.get_full_text_extent(line)[0]
                    if width > self.max_width:
                        line_words = []
                        for word in line.split():
                            line_words.append(word)
                            test_line = " ".join(line_words)
                            width = gc.get_full_text_extent(test_line)[0]
                            if width > self.max_width:
                                if len(line_words) > 1:
                                    lines.append(" ".join(line_words[:-1]))
                                    line_words = [word]
                                else:
                                    lines.append(word)
                                    line_words = []
                        if len(line_words) > 0:
                            lines.append(" ".join(line_words))
                    else:
                        lines.append(line)
            self.trait_setq(text="\n".join(lines))
            self._text_needs_fitting = False

    def _calc_line_positions(self, gc):
        if not self._position_cache_valid:
            with gc:
                gc.set_font(self.font)
                # The bottommost line starts at postion (0, 0).
                x_pos = []
                y_pos = []
                self._bounding_box = [0, 0]
                margin = self.margin
                prev_y_pos = margin
                prev_y_height = -self.line_spacing
                max_width = 0
                for line in self.text.split("\n")[::-1]:
                    if line != "":
                        (
                            width,
                            height,
                            descent,
                            leading,
                        ) = gc.get_full_text_extent(line)
                        ascent = height - abs(descent)
                        if width > max_width:
                            max_width = width
                        new_y_pos = (
                            prev_y_pos + prev_y_height + self.line_spacing
                        )
                    else:
                        # For blank lines, we use the height of the previous
                        # line, if there is one.  The width is 0.
                        leading = 0
                        if prev_y_height != -self.line_spacing:
                            new_y_pos = (
                                prev_y_pos + prev_y_height + self.line_spacing
                            )
                            ascent = prev_y_height
                        else:
                            new_y_pos = prev_y_pos
                            ascent = 0
                    x_pos.append(-leading + margin)
                    y_pos.append(new_y_pos)
                    prev_y_pos = new_y_pos
                    prev_y_height = ascent

            self._line_xpos = x_pos[::-1]
            self._line_ypos = y_pos[::-1]
            border_width = self.border_width if self.border_visible else 0
            self._bounding_box[0] = max_width + 2 * margin + 2 * border_width
            self._bounding_box[1] = (
                prev_y_pos + prev_y_height + margin + 2 * border_width
            )
            self._position_cache_valid = True
