############
How Do I...?
############

.. note::

    This section is currently under active development.

Basics
======

*How do I...*

* render data to an image file?::

    def save_plot(plot, filename, width, height):
        plot.outer_bounds = [width, height]
        plot.do_layout(force=True)
        gc = PlotGraphicsContext(size, dpi=72)
        gc.render_component(plot)
        gc.save(filename)

* render data to screen?
* integrate a Chaco plot into my WX app?
* integrate a Chaco plot into my Traits UI?
* make an application to render many streams of data?
* make a plot the right size?::

    def resize_plot(plot, width, height):
        plot.outer_bounds = [width, height]

* copy a plot the the clipboard?::

    def copy_to_clipboard(plot):
        # WX specific, though QT implementation is similar using 
        # QImage and QClipboard
        import wx

        width, height = plot.outer_bounds

        gc = PlotGraphicsContext((width, height), dpi=72)
        gc.render_component(plot_component)

        # Create a bitmap the same size as the plot 
        # and copy the plot data to it

        bitmap = wx.BitmapFromBufferRGBA(width+1, height+1, 
                                     gc.bmp_array.flatten())
        data = wx.BitmapDataObject()
        data.SetBitmap(bitmap)

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Unable to open the clipboard.", "Error")


Layout and Rendering
====================

*How do I...*

* put multiple plots in a single window?
* change the background color?
* turn off borders? 


Writing Components
==================

*How do I...*

* compose multiple renderers?
* write a custom renderer?
* write a custom overlay/underlay?
* write a custom tool?
* write a new container? 


Advanced
========

*How do I...*

* properly change/override draw dispatch?
* modify event dispatch?
* customize backbuffering?
* embed custom/native WX widgets on the plot? 

