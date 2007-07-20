"""
Defines the BaseDataRange class.
"""

# Enthought library imports
from enthought.traits.api import Event, HasTraits

# Local relative imports
from abstract_data_range import AbstractDataRange


class BaseDataRange(AbstractDataRange):
    """ Ranges represent sub-regions of data space.  
    
    They support "autoscaling" by querying their associated data sources.
    """

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------
    
    def __init__(self, *datasources, **kwtraits):
        super(AbstractDataRange, self).__init__(**kwtraits)
        if len(datasources) > 0:
            self.sources.extend(datasources)
    
    def add(self, *datasources):
        """ Convenience method to add a data source. """
        for datasource in datasources:
            if datasource not in self.sources:        
                self.sources.append(datasource)
    
    def remove(self, *datasources):
        """ Convenience method to remove a data source. """
        for datasource in datasources:
            if datasource in self.sources:
                self.sources.remove(datasource)

 

