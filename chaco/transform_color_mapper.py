from numpy import clip, ones_like

from chaco.api import ColorMapper
from traits.api import Trait, Callable, Tuple, Float, on_trait_change


class TransformColorMapper(ColorMapper):
    """This class adds arbitrary data transformations to a ColorMapper.
    
    The default ColorMapper is basically a linear mapper from data space to
    color space.  A TransformColorMapper allows a nonlinear mapper to be
    created.
    
    A ColorMapper works by linearly transforming the data from data space to the
    unit interval [0,1], and then linearly mapping that interval to the color
    space.
    
    A TransformColorMapper allows an arbitrary transform to be inserted at two
    places in this process.  First, an initial transformation, `data_func` can
    be applied to the data *before* is it mapped to [0,1].  Then another
    function, `unit_func`, can be applied to the transformed data on [0,1]
    before it is mapped to color space.  Normally, a `unit_func` is map of the
    unit interval [0,1] to itself (e.g. x^2 or sin(pi*x/2)).
    """

    data_func = Trait(None, None, Callable)
    
    unit_func = Trait(None, None, Callable)
    
    transformed_bounds = Tuple(Trait(None, None, Float),
                               Trait(None, None, Float))
    
    #-------------------------------------------------------------------
    # Trait handlers
    #-------------------------------------------------------------------       

    @on_trait_change('data_func, range.updated')
    def _update_transformed_bounds(self):

        if self.range is None:
            # The ColorMapper doesn't have a range yet, so don't do anything.
            # This apparently occurs during initialization.
            return
        if self.data_func is not None:
            low = self.range.low
            high = self.range.high
            trans_low = self.data_func(low)
            trans_high = self.data_func(high)
            self.transformed_bounds = (trans_low, trans_high)
        else:
            self.transformed_bounds = (None, None)
        self.updated = True

    def _unit_func_changed(self):
        self.updated = True

    #-------------------------------------------------------------------
    # Class methods
    #-------------------------------------------------------------------

    @classmethod
    def from_color_mapper(cls, color_mapper, data_func=None, unit_func=None,
                          **traits):
        """ Create a TransformColorMapper from an existing ColorMapper instance.
        """
        segdata = color_mapper._segmentdata
        return cls.from_segment_map(segdata, range=color_mapper.range,
                                    data_func=data_func, unit_func=unit_func,
                                    **traits)

    @classmethod
    def from_color_map(cls, color_map, data_func=None, unit_func=None,
                       **traits):
        """Create a TransformColorMapper from a colormap generator function.
        
        The return value is an instance of TransformColorMapper, *not* a factory
        function, so this does not provide a direct replacement for a standard
        colormap factory function.  For that, use the class method
        TransoformColorMapper.factory_from_color_map().
        """
        # Call the colormap factory function to create an instance of a
        # ColorMapper.
        color_mapper = color_map(None, **traits)
        segdata = color_mapper._segmentdata
        return cls.from_segment_map(segdata, range=color_mapper.range,
                                    data_func=data_func, unit_func=unit_func,
                                    **traits)

    @classmethod
    def factory_from_color_map(cls, color_map, data_func=None, unit_func=None,
                               **traits):
        """
        Create a TransformColorMapper factory function from a standard colormap
        factory function.
        
        WARNING: This function is untested; I realized I didn't need it shortly
        after writing it, so I haven't tried it yet. --WW
        """
        # Call the colormap factory function to create an instance of a
        # ColorMapper.
        color_mapper = color_map(None, **traits)

        def factory(range, **traits):
            tcm = cls.from_color_mapper(color_mapper,
                            data_func=data_func, unit_func=unit_func, **traits)
            return tcm

        return factory

    #-------------------------------------------------------------------
    # ColorMapper interface (these override methods from ColorMapper)
    #-------------------------------------------------------------------

    def map_screen(self, data_array):
        """ Maps an array of data values to an array of colors.
        """

        norm_data = self._compute_normalized_data(data_array)
        return self._map(norm_data)


    def map_index(self, data_array):
        """ Maps an array of values to their corresponding color band index. 
        """

        norm_data = self._compute_normalized_data(data_array)
        indices = (norm_data * (self.steps-1)).astype(int)
        return indices

    #-------------------------------------------------------------------
    # Private methods
    #-------------------------------------------------------------------

    def _compute_normalized_data(self, data_array):
        """
        Apply `data_func`, then linearly scale to the unit interval, and
        then apply `unit_func`.
        """
        
        # FIXME: Deal with nans?

        if self._dirty:
            self._recalculate()

        if self.data_func is not None:
            data_array = self.data_func(data_array)
            low, high = self.transformed_bounds
        else:
            low, high = self.range.low, self.range.high

        # Linearly transform the values to the unit interval.        
        if high == low:
            # Handle null range.
            norm_data = 0.5*ones_like(data_array)
        else:
            norm_data = clip((data_array - low) / (high - low), 0.0, 1.0)

        if self.unit_func is not None:
            norm_data = self.unit_func(norm_data)

        return norm_data
