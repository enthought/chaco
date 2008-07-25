#!/usr/bin/env python
#
# This tutorial shows how to open a WX window with a simple plot inside it.

import wx
from numpy import *
from enthought.chaco.api import *

# This is a little boilerplate main() function that runs the wx main event
# loop.  Note that we're using "PlotFrame" as the top-level frame for our
# application.  We'll actually define it later.
def main():
    app = wx.PySimpleApp()
    frame = PlotFrame(None)
    app.MainLoop()


# Now we'll define a wx Frame subclass and place our plot inside it.  Most of
# this code should be pretty familiar if you've dabbled with WX before.
# The only new thing is that we're going to import a Window from the Enable
# library, and embed our plot in that.  This Window object just allows our
# plot to look like a generic Panel to WX.
from enthought.enable.wx_backend.api import Window

class PlotFrame(wx.Frame):
    
    # This function creates some data and returns a Plot object.
    def make_plot(self):
        x = linspace(-2*pi, 2*pi, 200)
        y1 = sin(x)
        y2 = cos(x)
        pd = ArrayPlotData(x=x, y1=y1, y2=y2)

        myplot = Plot(pd)
        myplot.plot(("x", "y1"), type="line")
        myplot.plot(("x", "y2"), type="scatter")
        return myplot

    def __init__(self, *args, **kw):
        if "size" not in kw:
            kw["size"] = (600,600)
        wx.Frame.__init__(self, *args, **kw )
        
        # Create the Enable Window object.  The Window requires a WX parent
        # object as its first argument, so we just pass 'self'.
        win = Window(self, component = self.make_plot())
        
        # We'll create a default sizer and add the Window to it.  Since Window
        # is an Enable object, we need to get its corresponding WX control.
        # This is stored in its ".control" attribute.
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(win.control, 1, wx.EXPAND)
        
        # More WX boilerplate.
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Show(True)
        return
        
if __name__ == "__main__":
    main()

