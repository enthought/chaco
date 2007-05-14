#!/usr/bin/env python
#
#
# Tutorial 9b. Synchronize the Y data space as well,and add some tools.


from tutorial8 import PlotFrame
from enthought.chaco2.tools.api import SimpleZoom

class PlotFrame2(PlotFrame):
    def _create_plot(self):
        container = super(PlotFrame2, self)._create_plot()
        
        self.right_plot.index_mapper.range = self.left_plot.index_mapper.range
        self.right_plot.value_mapper.range = self.left_plot.value_mapper.range
        
        self.left_plot.overlays.append(SimpleZoom(self.left_plot, 
                tool_mode="box", always_on=False))
        self.right_plot.overlays.append(SimpleZoom(self.right_plot,
                tool_mode="box", always_on=False))

        return container

if __name__ == "__main__":
    import wx
    app = wx.PySimpleApp()
    frame = PlotFrame2(None)
    app.MainLoop()
