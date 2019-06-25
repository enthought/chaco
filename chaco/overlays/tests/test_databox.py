import numpy as np
import unittest

from traits.testing.api import UnittestTools

from chaco.api import (
    CMapImagePlot, GridDataSource, GridMapper, DataRange2D, ImageData
)
from chaco.overlays.databox import DataBox


class TestDataBox(unittest.TestCase, UnittestTools):
    """Test the DataBox"""
    def setUp(self):

        # Set up plot component containing
        xs = np.arange(0, 5)
        ys = np.arange(0, 5)

        index = GridDataSource(
            xdata=xs, ydata=ys, sort_order=('ascending', 'ascending'))

        index_mapper = GridMapper(range=DataRange2D(index))

        color_source = ImageData(data=np.ones(shape=(5, 5)), depth=1)

        self.plot = CMapImagePlot(
            index=index,
            index_mapper=index_mapper,
            value=color_source,
            orientation='h',
            origin='top left',
        )

        self.databox = DataBox(
            component=self.plot,
            data_position=[0, 0],
        )

        self.plot.overlays.append(self.databox)

    def test_update_data_position(self):
        """
        Test that data position property is updated properly when the position
            trait is changed.
        """

        # Check that data position property is changed when position is changed
        with self.assertTraitChanges(self.databox, 'data_position') as result:
            self.databox.position = [1, 1]

            # Without moving the DataBox, data_position trait defaults
            # to [0.0, 0.0]
            starting_position = [0.0, 0.0]
            expected = (
                self.databox,
                'data_position',
                starting_position,
                starting_position
            )
            self.assertSequenceEqual([expected], result.events)
