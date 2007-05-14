#!/usr/bin/env python
#
#
# Tutorial 9. Link the horizontal ranges of the two plots.


from tutorial8 import PlotFrame

class PlotFrame2(PlotFrame):
    def _create_plot(self):
        container = super(PlotFrame2, self)._create_plot()
        
        self.right_plot.index_mapper.range = self.left_plot.index_mapper.range
        
        return container

if __name__ == "__main__":
    import wx
    app = wx.PySimpleApp()
    frame = PlotFrame2(None)
    app.MainLoop()
