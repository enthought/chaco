"""
Defines markers classes, used by a variety of renderers.  
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
    """ Abstract class for markers.
    """
    # How this marker is to be stroked (from enthouhgt.kiva.constants).
    # Since this needs to be a class variable, it can't be a trait.
    draw_mode = STROKE
    #draw_mode = Enum(FILL, EOF_FILL, STROKE, FILL_STROKE, EOF_FILL_STROKE)
    
    # The kiva marker type (from enthought.kiva.constants).
    kiva_marker = NO_MARKER
    
    # Close the path object after drawing this marker?
    close_path = Bool(True)

    # Render the marker antialiased?  Some
    # markers render faster and look better if they are not anti-aliased..
    antialias = Bool(True)
    
    def add_to_path(self, path, size):
        """ Adds this marker's representation to *path*, scaled appropriately
        for *size*.
        
        Parameters
        ----------
        path : GraphicsContext
            The target for drawing the marker.
        size : number
            Size of the marker, in pixels
        """
        if self.close_path:
            self._add_to_path(path, size)
            path.close_path()
        else:
            self._add_to_path(path, size)
            
    def get_compiled_path(self, size):
        """ Returns a compiled path object that represents this marker, scaled
        appropriately for *size*.
        """
        raise NotImplementedError

    def _add_to_path(self, path, size):
        # subclasses must implement this method
        raise NotImplementedError


class SquareMarker(AbstractMarker):
    """ A marker that is a square.
    """
    # How this marker is to be stroked. (Overrides AbstractMarker.)
    draw_mode = FILL_STROKE
    # The Kiva marker type. (Overrides AbstractMarker.)
    kiva_marker = SQUARE_MARKER
    # Do not render anti-aliased. (Overrides AbstractMarker.)
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.rect( -size, -size, size * 2, size * 2 )

class DiamondMarker(AbstractMarker):
    """ A marker that is a diamond.
    """
    # How this marker is to be stroked. (Overrides AbstractMarker.)
    draw_mode = FILL_STROKE
    # The Kiva marker type. (Overrides AbstractMarker.)
    kiva_marker = DIAMOND_MARKER
    # Do not render anti-aliased. (Overrides AbstractMarker.)
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.lines( array( ( ( 0, -size ),
                             ( -size, 0 ),
                             ( 0, size ),
                             ( size, 0 ) ) ) )

class CircleMarker(AbstractMarker):
    """ A marker that is a circle.
    """
    # How this marker is to be stroked. (Overrides AbstractMarker.)
    draw_mode = FILL_STROKE
    # The Kiva marker type. (Overrides AbstractMarker.)
    kiva_marker = CIRCLE_MARKER
    # Array of points in a circle
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
    """ A marker that is a triangle with one apex pointing up.
    """
    # How this marker is to be stroked. (Overrides AbstractMarker.)
    draw_mode = FILL_STROKE
    # The Kiva marker type. (Overrides AbstractMarker.)
    kiva_marker = TRIANGLE_MARKER
    # Do not render anti-aliased. (Overrides AbstractMarker.)
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.lines( array( ( ( -size, -size ),
                             (  size, -size ),
                             (    0,  0.732 * size ) ) ) )

class Inverted_TriangleMarker(AbstractMarker):
    """ A marker that is a triangle with one apex pointing down.
    """
    # How this marker is to be stroked. (Overrides AbstractMarker.)
    draw_mode = FILL_STROKE
    # The Kiva marker type. (Overrides AbstractMarker.)
    kiva_marker = INVERTED_TRIANGLE_MARKER
    # Do not render anti-aliased. (Overrides AbstractMarker.)
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.lines( array( ( ( -size, size ),
                             (  size, size ),
                             (  0, -0.732 * size ) ) ) )

class PlusMarker(AbstractMarker):
    """ A marker that is a plus-sign.
    """
    # How this marker is to be stroked. (Overrides AbstractMarker.)
    draw_mode = STROKE
    # The Kiva marker type. (Overrides AbstractMarker.)
    kiva_marker = PLUS_MARKER
    # Do not render anti-aliased. (Overrides AbstractMarker.)
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.move_to( 0, -size )
        path.line_to( 0,  size )
        path.move_to( -size, 0 )
        path.line_to(  size, 0 )

class CrossMarker(AbstractMarker):
    """ A marker that is an X.
    """
    # How this marker is to be stroked. (Overrides AbstractMarker.)
    draw_mode = STROKE
    # The Kiva marker type. (Overrides AbstractMarker.)
    kiva_marker = CROSS_MARKER
    # Do not render anti-aliased. (Overrides AbstractMarker.)
    antialias = False
    
    def _add_to_path ( self, path, size ):
        path.move_to( -size, -size )
        path.line_to(  size,  size )
        path.move_to(  size, -size )
        path.line_to( -size,  size )

class DotMarker(AbstractMarker):
    """ A marker that is a dot.
    """
    # How this marker is to be stroked. (Overrides AbstractMarker.)
    draw_mode = FILL_STROKE
    # The Kiva marker type. (Overrides AbstractMarker.)
    kiva_marker = DOT_MARKER
    
    def _add_to_path ( self, path, size ):
        path.arc(0, 0, size, 0, 2*pi)

class PixelMarker(AbstractMarker):
    """ A marker that is a pixel.
    """
    # How this marker is to be stroked. (Overrides AbstractMarker.)
    draw_mode = STROKE
    # The Kiva marker type. (Overrides AbstractMarker.)
    kiva_marker = PIXEL_MARKER
    # Do not render anti-aliased. (Overrides AbstractMarker.)
    antialias = False
    
    def _add_to_path ( self, path, size ):
        # It's impossible to emulate a true Pixel Marker in a vector
        # system, so we just draw a sub-pixel square 1.0 unit across.
        path.rect(-0.5, -0.5, 1.0, 1.0)

class CustomMarker(AbstractMarker):
    """ A marker that is a custom shape.
    """
    # How this marker is to be stroked. (Overrides AbstractMarker.)
    draw_mode = STROKE
    # The Kiva marker type. (Overrides AbstractMarker.)
    kiva_marker = NO_MARKER
    
    # The custom path that represents this marker.
    path = Instance(CompiledPath)
    
    # Automatically scale **path** based on the input size parameter?
    # If False, then the path does not respond to the 'size' parameter!
    scale_path = Bool(True)
    
    def _add_to_path( self, path, size ):
        if self.scale_path:
            path.save_ctm()
            path.scale_ctm(size)
        path.add_path(path)
        if self.scale_path:
            path.restore_ctm()
    
    def get_compiled_path(self, size):
        """ Returns a path instance. 
        
        If **scale_path** is True, then the returned path is a new compiled
        path that is scaled based on *size*. If **scaled_path** is False,
        then this method just returns the current **path**.
        """
        if self.scale_path:
            newpath = CompiledPath()
            newpath.scale_ctm(size)
            newpath.add_path(self.path)
            return newpath
        else:
            return self.path

# String names for marker types.
marker_names = ("square", "circle", "triangle", "inverted_triangle", "plus",
                "cross", "diamond", "dot", "pixel")

# Mapping of marker string names to classes.
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

# A mapped trait that allows string naming of marker classes.
marker_trait = Trait("square", MarkerNameDict,
                     editor=EnumEditor(values=marker_names))


#EOF
