#!/usr/bin/env python
#
#
# Tutorial 7. Writing a tool (cont.) - Looking at data space

from enthought.chaco.api import AbstractController

class DataPrinter(AbstractController):
    def dispatch(self, event, suffix):
        x = self.component.x_mapper.map_data(event.x)
        y = self.component.y_mapper.map_data(event.y)
        print suffix, "event received at (%f,%f)" % (x, y)


from tutorial2 import myplot, PlotFrame, main

myplot.tools.append(DataPrinter(component=myplot))

if __name__ == "__main__":
    main()
