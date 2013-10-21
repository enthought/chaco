import contextlib
import unittest

import numpy

from chaco.api import ArrayPlotData
from traits.api import HasTraits, Instance, List, on_trait_change


class ArrayPlotDataEventsCollector(HasTraits):
    plot_data = Instance(ArrayPlotData)

    data_changed_events = List

    @on_trait_change('plot_data:data_changed')
    def _got_data_changed_event(self, event):
        self.data_changed_events.append(event)


class ArrayPlotDataTestCase(unittest.TestCase):
    @contextlib.contextmanager
    def monitor_events(self, plot_data):
        """
        Context manager to collect data_changed events.

        """
        collector = ArrayPlotDataEventsCollector(plot_data=plot_data)
        yield collector.data_changed_events

    def test_data_changed_events(self):
        # Test data.
        grumpy = numpy.ones((3, 4))
        grumpy_too = numpy.zeros(16)

        plot_data = ArrayPlotData()

        with self.monitor_events(plot_data) as events:
            plot_data.set_data('Grumpy', grumpy)
            self.assertEqual(events, [{'added': ['Grumpy']}])

        # While we're here, check that get_data works as advertised.
        grumpy_out = plot_data.get_data('Grumpy')
        self.assertIs(grumpy_out, grumpy)

        with self.monitor_events(plot_data) as events:
            plot_data.set_data('Grumpy', grumpy_too)
            self.assertEqual(events, [{'changed': ['Grumpy']}])

        with self.monitor_events(plot_data) as events:
            plot_data.del_data('Grumpy')
            self.assertEqual(events, [{'removed': ['Grumpy']}])


if __name__ == '__main__':
    import nose
    nose.run()
