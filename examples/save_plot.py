""" Demonstrates saving and loading plot configurations. """

# Major library imports
from cPickle import load, dump
import wx
from numpy import arange
from scipy.special import jn

# Enthought library imports
from enthought.enable2.wx_backend.api import Window
from enthought.enable2.example_support import DemoFrame, demo_main
from enthought.chaco2.api import OverlayPlotContainer, create_line_plot, \
                                 add_default_axes, add_default_grids
from enthought.chaco2.tools.api import PanTool, SimpleZoom


WILDCARD = "Saved plots (*.plt)|*.plt|"\
           "All files (*.*)|*.*"

class SavePlotDemoFrame(DemoFrame):

    def _create_menu_bar(self):
        menu = wx.Menu()
        menu.Append(101, "Load plot...")
        menu.Append(102, "Save plot...")
        self._menu_bar = wx.MenuBar()
        self._menu_bar.Append(menu, "File")
        self.Bind(wx.EVT_MENU, self.load_plot, id=101)
        self.Bind(wx.EVT_MENU, self.save_plot, id=102)
        return

    def load_plot(self, event):
        import os
        dlg = wx.FileDialog(self, "Select saved plot", defaultDir=os.getcwd(),
                            defaultFile="", wildcard=WILDCARD,
                            style=wx.OPEN | wx.CHANGE_DIR | wx.FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

            print "Loading plot", path, "..."
            try:
                f = file(path, "rb")
                del self.plot_container
                self.plot_container = load(f)
                self.plot_container._post_load()
                f.close()
            except:
                print "Error loading!"
                raise
            print "Plot loaded."
            dlg.Destroy()

            self.enable_win.component = self.plot_container
            self.plot_container.do_layout(force=True)
            self.plot_container.request_redraw()
            self.enable_win.control.Refresh()
            self.enable_win.control.Update()
        else:
            dlg.Destroy()

        return

    def save_plot(self, event):
        import os
        dlg = wx.FileDialog(self, "Save plot as...", defaultDir=os.getcwd(),
                            defaultFile="", wildcard=WILDCARD,
                            style=wx.SAVE | wx.CHANGE_DIR)  # | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

            print "Saving plot to", path, "..."
            try:
                f = file(path, "wb")
                dump(self.plot_container, f)
                f.close()
            except:
                print "Error saving!"
                raise
            print "Plot saved."
        dlg.Destroy()
        return

    def _create_window(self):
        container = self._create_plot_frame()
        self._create_menu_bar()
        self.SetMenuBar(self._menu_bar)
        self.enable_win = Window(self, -1, component=container)
        return self.enable_win

    def _create_plot_frame(self):
        container = OverlayPlotContainer(padding=50, fill_padding=True,
                                         bgcolor="lightgray", use_backbuffer=True)
        numpoints = 100
        low = -5
        high = 15.0
        x = arange(low, high, (high-low)/numpoints)

        # Plot some bessel functions
        value_range = None
        index_range = None
        for i in range(10):
            y = jn(i, x)
            plot = create_line_plot((x,y), color=(1.0-i/10.0,i/10.0,0,1), width=2.0)
            if i == 0:
                value_range = plot.value_mapper.range
                index_range = plot.index_mapper.range
                add_default_grids(plot)
                add_default_axes(plot)
                plot.tools.append(PanTool(plot))
                plot.overlays.append(SimpleZoom(plot))
            else:
                plot.value_mapper.range = value_range
                value_range.add(plot.value)
                plot.index_mapper.range = index_range
                index_range.add(plot.index)

            if i%2 == 1:
                plot.line_style = "dash"
            container.add(plot)

        self.plot_container = container
        return container


if __name__ == "__main__":
    print "!! Warning: This demo is buggy!"
    demo_main(SavePlotDemoFrame, size=(600,500), title="Simple line plot")

# EOF
