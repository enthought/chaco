"""Tutorial 4. Adding a zoom tool

The ZoomTool tool has a visual component, so it needs to be added to the
list of overlays instead of the list of bare tools.
"""

from enthought.chaco.tools.api import ZoomTool

from tutorial2 import demo

plot = demo.plot
plot.overlays.append(ZoomTool(plot, tool_mode="box", always_on=True))

if __name__ == "__main__":
    demo.configure_traits()
