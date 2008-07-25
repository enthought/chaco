"""
DataSeries are the most fundamental encapsulation of numerical data in Chaco.
They implement the DataSource interface and have a name and a dimension.

The best way to adapt external domain objects for Chaco is to make them
subclass AbstractDataSeries.  (An alternate approach is to make them produce
instances of a DataSeries subclass of the appropriate dimension.)
"""

from enthought.traits.api import Enum, Event, Instance

from datasource import DataSource

class AbstractDataSeries(DataSource):
    """
    Base class for all DataSeries.  Fleshes out some of the basic common
    functionality of DataSources when applied to numerical arrays.
    """
    # Re-declare the "parent" trait (inherited from DataSource) to indicate
    # that DataSeries are the start of the data pipeline.
    parent = None
    
    # Add some additional metadata that all DataSeries should have.
    metadata = Instance(dict, {"selections":[], "annotations":[]})

    def get_view(self):
        # If the upwards-propagating get_view() call has reached us, then there
        # were no ViewFilters downstream of us.  This method should do the right
        # thing for all standard, numerical DataSeries subclasses.
        return None

    
#EOF
