#!/usr/bin/env python
#
#
# Tutorial 5. Coordinating different tools

from tutorial2 import myplot, PlotFrame, main

from chaco.tools.api import PanTool, ZoomTool

# The ZoomTool tool has a visual component, so it needs to be added to the
# list of overlays instead of the list of bare tools.
myplot.tools.append(PanTool(myplot))
myplot.overlays.append(ZoomTool(myplot, tool_mode="box", always_on=False))

# And now we just run it.
if __name__ == "__main__":
    main()
