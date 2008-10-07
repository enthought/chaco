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
        gc.render_component((width, height))
        gc.save(filename)

* render data to screen?
* integrate a Chaco plot into my WX app?
* integrate a Chaco plot into my Traits UI?
* make an application to render many streams of data?::

    def plot_several_series(index, series_list):
        plot_data = ArrayPlotData(index=index)
        plot = Plot(plot_data)

        for i, data_series in enumerate(series_list):
            series_name = "series_%d" % i
            plot_data.set_data(series_name, data_series)
            plot.plot(('index', series_name))

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
* change the background color?::

    def make_black_plot(index, data_series):
        plot_data = ArrayPlotData(index=index)
        plot_data.set_data('data_series', data_series)
        plot = Plot(plot_data, bgcolor='black')
        plot.plot(('index', 'data_series'))

    def change_bgcolor(plot):
        plot.bgcolor = 'black'

* turn off borders? ::

    def make_borderless_plot(index, data_series):
        plot_data = ArrayPlotData(index=index)
        plot_data.set_data('data_series', data_series)
        plot = Plot(plot_data, border_visible=False)
        plot.plot(('index', 'data_series'))

    def change_to_borderless_plot(plot):
        plot.border_visible = False


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

