#!/usr/bin/env python
#
# This example extends the previous example and shows how different plots
# can be linked up by sharing DataRanges.

from tut2 import Tut2Frame

# Because we want the same basic plots as in tut2.py, we can directly
# subclass the Tut2Frame defined there and extend the make_plots()
# method a little bit.
class Tut3Frame(Tut2Frame):

    def make_plot(self):
        
        # Create the plots by calling the parent method:
        container = Tut2Frame.make_plot(self)

        # Grab the two plots out of the container and set their
        # ranges to be the same.
        plot1, plot2 = container.components
        plot2.value_range = plot1.value_range
        plot2.index_range = plot1.index_range
        return container

if __name__ == "__main__":
    import wx
    app = wx.PySimpleApp()
    frame = Tut3Frame(None, size=(1000,500))
    app.MainLoop()
