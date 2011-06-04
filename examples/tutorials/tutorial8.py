#!/usr/bin/env python
#
#
# Tutorial 8. Putting two plots on the screen
#
# This tutorial sets up for showing how Chaco allows easily opening multiple
# views into a single dataspace, which is demonstrated in later tutorials.


import wx
from scipy import arange
from scipy.special import jn
from chaco.api import *
from chaco.tools.api import *
from enable.api import Window

class PlotFrame(wx.Frame):
    def __init__(self, *args, **kw):
        kw["size"] = (850, 550)
        wx.Frame.__init__( *(self,) + args, **kw )
        self.plot_window = Window(self, component=self._create_plot())
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.plot_window.control, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Show(True)
        return

    def _create_plot(self):
        x = arange(-5.0, 15.0, 20.0/100)

        y = jn(0, x)
        left_plot = create_line_plot((x,y), bgcolor="white",
                                     add_grid=True, add_axis=True)
        left_plot.tools.append(PanTool(left_plot))
        self.left_plot = left_plot

        y = jn(1, x)
        right_plot = create_line_plot((x,y), bgcolor="white",
                                      add_grid=True, add_axis=True)
        right_plot.tools.append(PanTool(right_plot))
        right_plot.y_axis.orientation = "right"
        self.right_plot = right_plot

        # Tone down the colors on the grids
        right_plot.hgrid.line_color = (0.3,0.3,0.3,0.5)
        right_plot.vgrid.line_color = (0.3,0.3,0.3,0.5)
        left_plot.hgrid.line_color = (0.3,0.3,0.3,0.5)
        left_plot.vgrid.line_color = (0.3,0.3,0.3,0.5)

        container = HPlotContainer(spacing=20, padding=50, bgcolor="lightgray")
        container.add(left_plot)
        container.add(right_plot)
        return container

if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = PlotFrame(None)
    app.MainLoop()
