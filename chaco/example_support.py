# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

doc = """
This file contains a support class that wraps up the boilerplate toolkit calls
that virtually all the demo programs have to use, and doesn't actually do
anything when run on its own.

Try running simple_line.py, colormapped_scatter.py, or check out any of
the programs in in tutorials/.
"""
from numpy import array

from traits.etsconfig.api import ETSConfig


# Import a default palette for backwards compatibility
from .default_colors import cbrewer as COLOR_PALETTE


# FIXME - it should be enough to do the following import, but because of the
# PyQt/traits problem (see below) we can't because it would drag in traits too
# early.  Until it is fixed we just assume wx if we can import it.
# Force the selection of a valid toolkit.
if not ETSConfig.toolkit:
    for toolkit, toolkit_module in (("wx", "wx"), ("qt4", "pyface.qt")):
        try:
            __import__(toolkit_module)
            ETSConfig.toolkit = toolkit
            break
        except ImportError:
            pass
    else:
        raise RuntimeError("Can't load wx or qt4 backend for Chaco.")


if ETSConfig.toolkit == "wx":
    import wx

    class DemoFrame(wx.Frame):
        """Wraps boilerplate WX calls that almost all the demo programs have
        to use.
        """

        def __init__(self, *args, **kw):
            wx.Frame.__init__(*(self,) + args, **kw)
            self.SetAutoLayout(True)

            # Create the subclass's window
            self.plot_window = self._create_window()

            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(self.plot_window.control, 1, wx.EXPAND)
            self.SetSizer(sizer)
            self.Show(True)

        def _create_window(self):
            "Subclasses should override this method and return an enable.wx.Window"
            raise NotImplementedError

    def demo_main(demo_class, size=(400, 400), title="Chaco plot"):
        "Takes the class of the demo to run as an argument."
        app = wx.PySimpleApp()
        frame = demo_class(None, size=size, title=title)
        app.SetTopWindow(frame)
        app.MainLoop()


elif ETSConfig.toolkit == "qt4":
    from pyface.qt import QtGui

    _app = QtGui.QApplication.instance()

    if _app is None:
        import sys

        _app = QtGui.QApplication(sys.argv)

    class DemoFrame(QtGui.QWidget):
        def __init__(self, parent, **kw):
            QtGui.QWidget.__init__(self)

            # Create the subclass's window
            self.plot_window = self._create_window()

            layout = QtGui.QVBoxLayout()
            layout.setMargin(0)
            layout.addWidget(self.plot_window.control)

            self.setLayout(layout)

            if "size" in kw:
                self.resize(*kw["size"])

            if "title" in kw:
                self.setWindowTitle(kw["title"])

            self.show()

        def _create_window(self):
            "Subclasses should override this method and return an enable.Window"
            raise NotImplementedError

    def demo_main(demo_class, size=(400, 400), title="Chaco plot"):
        "Takes the class of the demo to run as an argument."
        frame = demo_class(None, size=size, title=title)
        _app.exec_()


elif ETSConfig.toolkit == "pyglet":
    from enable.pyglet_backend.pyglet_app import get_app, PygletApp

    class DemoFrame(object):
        def __init__(self):
            app = get_app()
            if app:
                window = self._create_window()
                self.enable_win = window
                app.add_window(window.control)

        def _create_window(self):
            raise NotImplementedError

    def demo_main(demo_class, size=(640, 480), title="Chaco Example"):
        """Runs a simple application in Pyglet using an instance of
        **demo_class** as the main window or frame.

        **demo_class** should be a subclass of DemoFrame or the pyglet
        backend's Window class.
        """
        app = PygletApp()
        if issubclass(demo_class, DemoFrame):
            frame = demo_class()
            window = frame.enable_win.control
        else:
            window = demo_class().control
        if not window._fullscreen:
            window.set_size(*size)
        window.set_caption(title)
        app.set_main_window(window)
        app.run()


if __name__ == "__main__":
    print("\n" + doc + "\n")
