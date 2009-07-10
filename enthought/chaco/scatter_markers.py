# This module used to be the home of the various Marker classes, but they
# have since been moved to the enable.markers module.

from enthought.enable.markers import AbstractMarker, SquareMarker, \
    CircleMarker, TriangleMarker, Inverted_TriangleMarker, PlusMarker, \
    CrossMarker, DiamondMarker, DotMarker, PixelMarker, CustomMarker, \
    marker_trait, MarkerNameDict, marker_names

from enthought.kiva.constants import STROKE, FILL_STROKE, \
            SQUARE_MARKER, DIAMOND_MARKER, CIRCLE_MARKER, \
            CROSS_MARKER, TRIANGLE_MARKER, \
            INVERTED_TRIANGLE_MARKER, PLUS_MARKER, DOT_MARKER, \
            PIXEL_MARKER, NO_MARKER

from enthought.kiva import CompiledPath


