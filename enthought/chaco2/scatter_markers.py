"""
Defines markers classes, used by a variety of renderers.  Also defines
marker_trait, a MappedTrait that allows string naming of marker classes.
"""

# Major library imports
from numpy import array, pi

# Enthought library imports
from enthought.traits.api import HasTraits, Bool, Enum, Instance, Trait
from enthought.traits.ui.api import EnumEditor
from enthought.kiva.constants import FILL, EOF_FILL, STROKE, FILL_STROKE, \
            EOF_FILL_STROKE, SQUARE_MARKER, DIAMOND_MARKER, CIRCLE_MARKER, \
            CROSSED_CIRCLE_MARKER, CROSS_MARKER, TRIANGLE_MARKER, \
            INVERTED_TRIANGLE_MARKER, PLUS_MARKER, DOT_MARKER, \
            PIXEL_MARKER, NO_MARKER
from enthought.kiva import CompiledPath



class AbstractMarker(HasTraits):
    
    # How this marker should be stroked.  (These are Kiva constants.)
    # Since we want this to be a class variable, we can't make it a trait
    #draw_mode = Enum(FILL, EOF_FILL, STROKE, FILL_STROKE, EOF_FILL_STROKE)
    draw_mode = STROKE
    
    # The kiva marker type (enthought.kiva.constants)
    kiva_marker = NO_MARKER
    
    # Whether or not to close out the path object after drawing this path.
    close_path = Bool(True)

    # Whether or not the marker should be rendered antialiased.  Some
    # markers render faster and look better pixelated.
    antialias = Bool(True)
    
    def add_to_path(self, path, size):
        """
        Adds this marker's representation to 'path', scaled appropriately
        for the input size.
        """
        if self.close_path:
            self._add_to_path(path, size)
            path.close_path()
        else:
            self._add_to_path(path, size)
            
    def get_compiled_path(self, size):
        """
        Returns a compiled path object that represents this path, scaled
        appropriately for the input size.
        """
        raise NotImplementedError

    def _add_to_path(self, path, size):
        # subclasses must implement this method
        raise NotImplementedError


class SquareMarker(AbstractMarker):
    
    draw_mode = FILL_STROKE
    kiva_marker = SQUARE_MARKER
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.rect( -size, -size, size * 2, size * 2 )

class DiamondMarker(AbstractMarker):
    
    draw_mode = FILL_STROKE
    kiva_marker = DIAMOND_MARKER
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.lines( array( ( ( 0, -size ),
                             ( -size, 0 ),
                             ( 0, size ),
                             ( size, 0 ) ) ) )

class CircleMarker(AbstractMarker):
    
    draw_mode = FILL_STROKE
    kiva_marker = CIRCLE_MARKER
    
    circle_points = array([[ 1.   ,  0.   ],
                           [ 0.966,  0.259],
                           [ 0.866,  0.5  ],
                           [ 0.707,  0.707],
                           [ 0.5  ,  0.866],
                           [ 0.259,  0.966],
                           [ 0.   ,  1.   ],
                           [-0.259,  0.966],
                           [-0.5  ,  0.866],
                           [-0.707,  0.707],
                           [-0.866,  0.5  ],
                           [-0.966,  0.259],
                           [-1.   ,  0.   ],
                           [-0.966, -0.259],
                           [-0.866, -0.5  ],
                           [-0.707, -0.707],
                           [-0.5  , -0.866],
                           [-0.259, -0.966],
                           [ 0.   , -1.   ],
                           [ 0.259, -0.966],
                           [ 0.5  , -0.866],
                           [ 0.707, -0.707],
                           [ 0.866, -0.5  ],
                           [ 0.966, -0.259],
                           [ 1.   , 0.    ]])
    
    def _add_to_path ( self, path, size ):
        if size <= 5:
            pts = self.circle_points[::3] * size
        elif size <= 10:
            pts = self.circle_points[::2] * size
        else:
            pts = self.circle_points * size
        path.lines(pts)


class TriangleMarker(AbstractMarker):
    
    draw_mode = FILL_STROKE
    kiva_marker = TRIANGLE_MARKER
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.lines( array( ( ( -size, -size ),
                             (  size, -size ),
                             (    0,  0.732 * size ) ) ) )

class Inverted_TriangleMarker(AbstractMarker):
    
    draw_mode = FILL_STROKE
    kiva_marker = INVERTED_TRIANGLE_MARKER
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.lines( array( ( ( -size, size ),
                             (  size, size ),
                             (  0, -0.732 * size ) ) ) )

class PlusMarker(AbstractMarker):
    
    draw_mode = STROKE
    kiva_marker = PLUS_MARKER
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.move_to( 0, -size )
        path.line_to( 0,  size )
        path.move_to( -size, 0 )
        path.line_to(  size, 0 )

class CrossMarker(AbstractMarker):
    
    draw_mode = STROKE
    kiva_marker = CROSS_MARKER
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.move_to( -size, -size )
        path.line_to(  size,  size )
        path.move_to(  size, -size )
        path.line_to( -size,  size )

class DotMarker(AbstractMarker):
    
    draw_mode = FILL_STROKE
    kiva_marker = DOT_MARKER
    
    def _add_to_path ( self, path, size ):
        path.arc(0, 0, size, 0, 2*pi)

class PixelMarker(AbstractMarker):
    
    draw_mode = STROKE
    kiva_marker = PIXEL_MARKER
    antialias = False
    
    def _add_to_path ( self, path, size ):
        # It's impossible to emulate a true Pixel Marker in a vector
        # system, so we just draw a sub-pixel square 1.0 unit across.
        path.rect(-0.5, -0.5, 1.0, 1.0)

class CustomMarker(AbstractMarker):
    
    draw_mode = STROKE
    kiva_marker = NO_MARKER
    
    # The custom path this represents.
    path = Instance(CompiledPath)
    
    # Whether or not this class should use a CTM to automatically scale
    # self.path based on the input size parameter.  If this is set to
    # False, then the path will not respond to the 'size' parameter!
    scale_path = Bool(True)
    
    def _add_to_path( self, path, size ):
        if self.scale_path:
            path.save_ctm()
            path.scale_ctm(size)
        path.add_path(path)
        if self.scale_path:
            path.restore_ctm()
    
    def get_compiled_path(self, size):
        if self.scale_path:
            newpath = CompiledPath()
            newpath.scale_ctm(size)
            newpath.add_path(self.path)
            return newpath
        else:
            return self.path

marker_names = ("square", "circle", "triangle", "inverted_triangle", "plus",
                "cross", "diamond", "dot", "pixel")

MarkerNameDict = {"square": SquareMarker,
                  "circle": CircleMarker,
                  "triangle": TriangleMarker,
                  "inverted_triangle": Inverted_TriangleMarker,
                  "plus": PlusMarker,
                  "cross": CrossMarker,
                  "diamond": DiamondMarker,
                  "dot": DotMarker,
                  "pixel": PixelMarker,
                  "custom": CustomMarker }

marker_trait = Trait("square", MarkerNameDict,
                     editor=EnumEditor(values=marker_names))


#EOF
