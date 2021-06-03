# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

X_PARAMS = (0, 2)  # index for x-position and width
Y_PARAMS = (1, 3)  # index for y-position and height


def trim_screen_rect(screen_rect, view_rect, sub_array_size):
    """Trim sub-image screen rectangle for highly zoomed in states.

    When zoomed into one or two pixels (in any dimension), the screen rectangle
    for those pixels can extend without bound outside of the plot area. This
    function will return altered bounds to remove unnecessary rendering.
    """
    screen_rect = list(screen_rect)  # Copy values that we'll be modifying.

    for n_px, (i_pos, i_length) in zip(sub_array_size, (X_PARAMS, Y_PARAMS)):
        if n_px == 1:
            screen_max = screen_rect[i_pos] + screen_rect[i_length]
            view_max = view_rect[i_pos] + view_rect[i_length]
            # Viewer bounds shows single pixel, so we can clip the actual pixel
            # bounds to the viewer bounds.
            new_min = max(screen_rect[i_pos], view_rect[i_pos])
            new_max = min(screen_max, view_max)
            screen_rect[i_pos] = new_min
            screen_rect[i_length] = new_max - new_min
        elif n_px == 2:
            image_length = screen_rect[i_length]
            # Viewer displays 2 pixels; if we scale down the sub-image's screen
            # size to twice the viewer size, we can be sure that any offset
            # will cover the entire screen.
            scale = 2 * view_rect[i_length] / float(image_length)
            if scale < 1:
                # Sub-image is two pixels wide, so pixel size is half the image
                pixel_length = image_length / 2
                screen_rect[i_length] *= scale
                screen_rect[i_pos] += (1 - scale) * pixel_length
    return screen_rect
