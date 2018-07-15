import contextlib
import unittest

import numpy as np
from numpy.testing import assert_array_equal

from chaco.api import DataFramePlotData
from traits.api import HasTraits, Instance, List, on_trait_change


class DataFramePlotDataEventsCollector(HasTraits):
    plot_data = Instance(DataFramePlotData)

    data_changed_events = List

    @on_trait_change('plot_data:data_changed')
    def _got_data_changed_event(self, event):
        self.data_changed_events.append(event)


@contextlib.contextmanager
def monitor_events(plot_data):
    """
    Context manager to collect data_changed events.

    """
    collector = DataFramePlotDataEventsCollector(plot_data=plot_data)
    yield collector.data_changed_events


try:
    from pandas import DataFrame


    class DataFramePlotDataTestCase(unittest.TestCase):

        def test_data_changed_events(self):
            # Test data.
            arr = np.zeros(16)
            arr2 = np.ones(16)

            df = DataFrame(index=np.arange(16))
            plot_data = DataFramePlotData(data_frame=df)

            assert_array_equal(plot_data.get_data('index'), df.index.values)

            with monitor_events(plot_data) as events:
                plot_data.set_data('arr', arr)
                self.assertEqual(events, [{'added': ['arr']}])

                assert_array_equal(df['arr'].values, arr)

                # While we're here, check that get_data works as advertised.
                out = plot_data.get_data('arr')
                assert_array_equal(arr, out)

            with monitor_events(plot_data) as events:
                plot_data.set_data('arr', arr2)
                self.assertEqual(events, [{'changed': ['arr']}])
                assert_array_equal(df['arr'].values, arr2)

            with monitor_events(plot_data) as events:
                plot_data.del_data('arr')
                self.assertEqual(events, [{'removed': ['arr']}])

        def test_no_index_column(self):
            # Test data.
            idx = np.arange(16)
            arr = np.zeros(16)
            df = DataFrame(index=idx)
            plot_data = DataFramePlotData(data_frame=df)

            assert_array_equal(plot_data.get_data('index'), df.index.values)

            # Can set 'index'
            with monitor_events(plot_data) as events:
                plot_data.set_data('index', arr)
                self.assertEqual(events, [{'changed': ['index']}])
                self.assertNotIn('index', df.columns)
                assert_array_equal(df.index.values, arr)

            # Cannot remove 'index' column
            with self.assertRaises(KeyError):
                plot_data.del_data('index')

        def test_index_column(self):
            # Test data.
            idx = np.arange(16)
            arr = np.zeros(16)
            arr2 = np.ones(16)
            data = {'index': arr}
            df = DataFrame(data, index=idx)
            plot_data = DataFramePlotData(data_frame=df)

            assert_array_equal(plot_data.get_data('index'), df['index'].values)

            # Can set 'index' column
            with monitor_events(plot_data) as events:
                plot_data.set_data('index', arr2)
                self.assertEqual(events, [{'changed': ['index']}])
                assert_array_equal(df['index'].values, arr2)

            # Can remove 'index' column
            with monitor_events(plot_data) as events:
                plot_data.del_data('index')
                self.assertNotIn('index', df.columns)
                # Since there is always an index, this will register a 'changed'
                # event instead of a 'removed' event.
                self.assertEqual(events, [{'changed': ['index']}])
                assert_array_equal(plot_data.get_data('index'), df.index.values)

except ImportError:
    raise unittest.SkipTest(
        "Cannot import pandas. Skipping all tests"
    )
