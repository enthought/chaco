#!/usr/bin/env python
#
#
# Tutorial 10. Demonstration that the views are linked, but the
#              data is not.


from tutorial9b import PlotFrame2
from enthought.chaco.tools.api import LineInspector

class PlotFrame3(PlotFrame2):
    def _create_plot(self):
        container = super(PlotFrame3, self)._create_plot()
        
        self.left_plot.overlays.append(LineInspector(component=self.left_plot,
                write_metadata=True, is_listener=True))
        
        self.right_plot.overlays.append(LineInspector(component=self.right_plot,
                write_metadata=True, is_listener=True))
        return container

if __name__ == "__main__":
    import wx
    app = wx.PySimpleApp()
    frame = PlotFrame3(None)
    app.MainLoop()
