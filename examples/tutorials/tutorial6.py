#!/usr/bin/env python
#
#
# Tutorial 6. Writing a tool

from chaco.api import AbstractController

# This interactor just prints out all the events it receives
class EventPrinter(AbstractController):
    def dispatch(self, event, suffix):
        print suffix, "event received at (%d,%d)" % (event.x, event.y)


from tutorial2 import myplot, PlotFrame, main

myplot.tools.append(EventPrinter(myplot))


if __name__ == "__main__":
    main()
