#!/usr/bin/env python
#
#
# Tutorial 4. Adding a zoom tool

from tutorial2 import myplot, PlotFrame, main

from enthought.chaco.tools.api import ZoomTool

# The ZoomTool tool has a visual component, so it needs to be added to the
# list of overlays instead of the list of bare tools.
myplot.overlays.append(ZoomTool(myplot, tool_mode="box", always_on=True))

# And now we just run it.
if __name__ == "__main__":
    main()

