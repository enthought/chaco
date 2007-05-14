"""Implements a structured gridded 2D data source (suitable as an index
for an image, for exmaple)
"""

# Major library imports
from numpy import array

# Enthougth library imports
from enthought.traits.api import Constant, Instance, Tuple

# Chaco imports
from abstract_data_source import AbstractDataSource
from array_data_source import ArrayDataSource
from base import SortOrderTrait


class GridDataSource(AbstractDataSource):

    
    #------------------------------------------------------------------------
    # AbstractDataSource traits
    #------------------------------------------------------------------------
    
    # Redefine the index dimension from the parent class.
    index_dimension = Constant('image')
    
    # Redefine the value dimension from the parent class
    value_dimension = Constant('scalar')
    
    # No overall sort order on 2D data, although for gridded 2D data, each
    # axis may have a sort order
    sort_order =Tuple(SortOrderTrait, SortOrderTrait)
 
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
   
    # data grid tics along the x (horizontal) axis 
    _xdata = Instance(ArrayDataSource, args=())

    # data grid tics along the y (vertical) axis 
    _ydata = Instance(ArrayDataSource, args=())

    # caches the value of min and max as long as data doesn't change
    _cached_bounds = Tuple
    
    
    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------
    
    def __init__(self, xdata=array([]), ydata=array([]), 
                       sort_order=("none","none"), **kwargs):
        super(GridDataSource, self).__init__(**kwargs)
        self.set_data(xdata, ydata, sort_order)

    def set_data(self, xdata, ydata, sort_order=None):
        if sort_order is not None:
            self._xdata.set_data(xdata, sort_order[0])
            self._ydata.set_data(ydata, sort_order[1])
        else:
            self._xdata.set_data(xdata)
            self._ydata.set_data(ydata)
        self._compute_bounds()
        self.data_changed = True

   
    #------------------------------------------------------------------------
    # AbstractDataSource interface
    #------------------------------------------------------------------------

    def get_data(self):
        """get_data() -> (xdata, ydata)

        Since we have structured (gridded) data, we return the pair of data
        axes, instead of, say, a full meshgrid. This behavious differs from 
        other data sources.
        """
        if self._xdata is not None:
            xdata = self._xdata
        else:
            xdata = ArrayDataSource(array([]))

        if self._ydata is not None:
            ydata = self._ydata
        else:
            ydata = ArrayDataSource(array([]))

        return xdata, ydata

    def get_bounds(self):
        """get_bounds() -> ((LLx, LLy), (URx, URy))
        
        Returns two 2D points, min and max, that represent the bounding
        corners of a rectangle enclosing the data set.  Note that these values
        are not view-dependent, but represent intrinsic properties of the
        DataSource.
        
        If data axis is the empty set, then the min and max vals are 0.0.
        """
        if self._cached_bounds == ():
            self._compute_bounds()
        return self._cached_bounds
        

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _compute_bounds(self, data=None):
        """
        Computes the minimum and maximum points (LLx, LLy) and (URx, URy) of 
        data.  
        """
        
        if data is None:
            xdata, ydata = self.get_data()
        else:
            xdata, ydata = data

        xbds = xdata.get_bounds()
        ybds = ydata.get_bounds()
    
        self._cached_bounds = ((xbds[0], ybds[0]), (xbds[1], ybds[1]))

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _metadata_changed(self, event):
        self.metadata_changed = True

    def _metadata_items_changed(self, event):
        self.metadata_changed = True



        

