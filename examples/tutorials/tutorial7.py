"""Tutorial 7. Writing a tool (cont.) - Looking at data space"""
from __future__ import print_function

from chaco.api import AbstractController

from tutorial2 import demo

class DataPrinter(AbstractController):
    def dispatch(self, event, suffix):
        x = self.component.x_mapper.map_data(event.x)
        y = self.component.y_mapper.map_data(event.y)
        print(suffix, "event received at (%f,%f)" % (x, y))

plot = demo.plot
plot.tools.append(DataPrinter(component=plot))

if __name__ == "__main__":
    demo.configure_traits()
