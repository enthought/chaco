
# Local relative imports
from plot_component import PlotComponent

class AbstractPlotRenderer(PlotComponent):
    """
    Defines AbstractPlotRenderer, the minimal interface that all plot renderers
    should support.  Higher-dimensionality plot renderers may have implement a
    richer subclass of AbstractPlotRenderer.
    
    This interface is mostly to support the development of generic interactors
    and plot tools.
    """

    #------------------------------------------------------------------------
    # Override default values of inherited traits PlotComponent
    #------------------------------------------------------------------------
    
    resizable = "hv"
    bgcolor = "transparent"


    def map_screen(self, data_array):
        """
        Maps an array of data points into screen space and returns it as an
        array.
        """
        raise NotImplementedError
    
    def map_data(self, screen_pt):
        """
        Maps a screen space point (sx,sy) into the *index* space of the plot.
        Note that this returns a floating point number, *not* an integer index.
        """
        raise NotImplementedError
    
    def map_index(self, screen_pt, threshold=0.0, outside_returns_none=True, \
                  index_only = False):
        """
        Returns an index into the plot's index array(s).  Typically this is
        just an integer but if the plot has 2D index dimension, then returns a
        tuple of ints.  If threshold is non-zero, then searches within the given
        screen-space threshold.  (This is useful for sparse 2D data.)
        
        If screen_pt is outside the range of the data, then returns either the
        appropriate end index or None, depending on "outside_returns_none".
        
        If index_only is True, then just maps based on the index coordinate of
        screen_pt, and ignores the value coordinate.
        
        If the input point cannot be mapped to an index, then None is returned.
        
        If screen_pt corresponds to multiple indices, then only the first index
        is returned.
        """
        raise NotImplementedError

    def _render_icon(self, gc, x, y, width, height):
        """
        Renders a representation of this plot as an icon into the box defined
        by the given coordinates.  Used by the legend.
        """
        pass


# EOF
