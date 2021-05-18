"""Tutorial 5. Coordinating different tools

We can add multiple tools on the sample plot
"""

from tutorial2 import demo

from chaco.tools.api import PanTool, ZoomTool

plot = demo.plot
plot.tools.append(PanTool(plot))
plot.overlays.append(ZoomTool(plot, tool_mode="box", always_on=False))

if __name__ == "__main__":
    demo.configure_traits()
