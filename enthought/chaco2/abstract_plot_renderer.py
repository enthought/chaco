""" Defines a base class for plot renderers.
"""
# Enthought library imports.
from enthought.traits.api import Enum

# Local relative imports
from plot_component import PlotComponent

class AbstractPlotRenderer(PlotComponent):
    """ This is the minimal interface that all plot renderers must support.  
    
    Higher-dimensionality plot renderers can implement a richer subclass of 
    this abstract class.
    
    This interface exists mostly to support the development of generic 
    interactors and plot tools.
    """

    origin = Enum("bottom left", "top left", "bottom right", "top right")

    #------------------------------------------------------------------------
    # Override default values of inherited traits PlotComponent
    #------------------------------------------------------------------------
    
    # Overrides the default value inherited from PlotComponent.
    bgcolor = "transparent"

    # Overrides the default value inherited from PlotComponent.
    resizable = "hv"


    def map_screen(self, data_array):
        """ Maps an array of data points to screen space and returns an array 
        of screen space points.
        """
        raise NotImplementedError
    
    def map_data(self, screen_pt):
        """ Maps a screen space point (sx, sy) to the "index" space of the plot.
        
        Returns a floating point number, *not* an integer index.
        """
        raise NotImplementedError
    
    def map_index(self, screen_pt, threshold=0.0, outside_returns_none=True, \
                  index_only = False):
        """ Maps a screen space point to an index into the plot's index array(s).  
        
        Parameters
        ----------
        screen_pt : (x,y)
            The screen space point to map.
        threshold : float
            Optional screen-space distance allowed between *screen_pt* and the
            plot; if non-zero, then a *screen_pt* within this distance is
            mapped to the neared plot index. (This feature is useful for sparse
            2-D data.)
        outside_returns_none : Boolean
            If True, then if *screen_pt* is outside the range of the data, the
            method returns None. If False, it returns the nearest end index in
            such a case.
        index_only : Boolean
            If True, then this method maps based only on the index coordinate 
            of *screen_pt*, and ignores the value coordinate.
        
        Returns
        -------
        An index into the plot's index array(s). Typically this index is just 
        an integer, but if the plot has a 2-D index dimension, then this method
        returns a tuple of integers. If the input point cannot be mapped to an
        index, then None is returned.
        
        If *screen_pt* corresponds to multiple indices, then only the first 
        index is returned.
        """
        raise NotImplementedError

    def _render_icon(self, gc, x, y, width, height):
        """ Renders an icon for this plot.
        
        This method is used by the legend to draw representation of this plot
        as an icon into the box defined by the given coordinates. 
        """
        pass


# EOF
