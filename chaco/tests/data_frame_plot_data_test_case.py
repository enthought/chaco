import contextlib
from traits.testing.unittest_tools import unittest

import numpy as np
from numpy.testing import assert_array_equal
from pandas import DataFrame

from chaco.api import DataFramePlotData
from traits.api import HasTraits, Instance, List, on_trait_change


class DataFramePlotDataEventsCollector(HasTraits):
    plot_data = Instance(DataFramePlotData)

    data_changed_events = List

    @on_trait_change('plot_data:data_changed')
    def _got_data_changed_event(self, event):
        self.data_changed_events.append(event)


class DataFramePlotDataTestCase(unittest.TestCase):

    @contextlib.contextmanager
    def monitor_events(self, plot_data):
        """
        Context manager to collect data_changed events.

        """
        collector = DataFramePlotDataEventsCollector(plot_data=plot_data)
        yield collector.data_changed_events

    def test_data_changed_events(self):
        # Test data.
        arr = np.zeros(16)
        arr2 = np.ones(16)

        df = DataFrame(index=np.arange(16))
        plot_data = DataFramePlotData(data_frame=df)

        assert_array_equal(plot_data.get_data('index'), df.index.values)

        with self.monitor_events(plot_data) as events:
            plot_data.set_data('arr', arr)
            self.assertEqual(events, [{'added': ['arr']}])

            assert_array_equal(df['arr'].values, arr)

            # While we're here, check that get_data works as advertised.
            out = plot_data.get_data('arr')
            assert_array_equal(arr, out)

        with self.monitor_events(plot_data) as events:
            plot_data.set_data('arr', arr2)
            self.assertEqual(events, [{'changed': ['arr']}])
            assert_array_equal(df['arr'].values, arr2)

        with self.monitor_events(plot_data) as events:
            plot_data.del_data('arr')
            self.assertEqual(events, [{'removed': ['arr']}])


if __name__ == '__main__':
    import nose
    nose.run()
