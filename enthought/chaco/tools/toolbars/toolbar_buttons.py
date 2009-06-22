import wx

from enthought.enable.tools.toolbars.toolbar_buttons import Button
from enthought.chaco.tools.simple_zoom import SimpleZoom
from enthought.chaco.api import PlotGraphicsContext
from enthought.kiva.backend_image import Image
from enthought.pyface.image_resource import ImageResource
from enthought.pyface.api import FileDialog, OK
from enthought.traits.api import Instance, Str, File
from enthought.traits.ui.api import View, Item

class ToolbarButton(Button):
    image = Str()
    _image = Instance(Image)

    color = 'white'


    def __init__(self, *args, **kw):
        super(ToolbarButton, self).__init__(*args, **kw)

        image_resource = ImageResource(self.image)
        self._image = Image(image_resource.absolute_path)

        self.height = self._image.height()
        self.width = self._image.width()

    def _draw_actual_button(self, gc):
        gc.draw_image(self._image,
                      (self.x, self.y+2, self._image.width(), self._image.height()))

class IndexAxisLogButton(ToolbarButton):
    label = 'Change index axis scale'
    image = 'zoom-fit-width'

    def perform(self, event):
        if self.container.component.index_scale == 'linear':
            self.container.component.index_scale = 'log'
        else:
            self.container.component.index_scale = 'linear'
        return

class ValueAxisLogButton(ToolbarButton):
    label = 'Change value axis scale'
    image = 'zoom-fit-height'

    def perform(self, event):
        if self.container.component.value_scale == 'linear':
            self.container.component.value_scale = 'log'
        else:
            self.container.component.value_scale = 'linear'
        return

class ZoomResetButton(ToolbarButton):
    label = 'Zoom reset'
    image = 'zoom-original'

    def perform(self, event):
        plot_component = self.container.component

        for overlay in plot_component.overlays:
            if isinstance(overlay, SimpleZoom):
                overlay._reset_state_pressed()



class SaveAsButton(ToolbarButton):
    label = 'Save As'
    image = 'document-save'

    def perform(self, event):
        plot_component = self.container.component

        filter = 'PNG file (*.png)|*.png|\nTIFF file (*.tiff)|*.tiff|'
        dialog = FileDialog(action='save as', wildcard=filter)

        if dialog.open() != OK:
            return

        filename = dialog.path

        # We need to hide the toolbar, then put it back after the
        # plot has been saved
        auto_hide_reset = plot_component.auto_hide
        plot_component.auto_hide = True

        width, height = plot_component.outer_bounds

        gc = PlotGraphicsContext((width, height), dpi=72)
        gc.render_component(plot_component)
        gc.save(filename)

        # Reset the auto_hide trait so the toolbar is no longer hidden
        plot_component.auto_hide = auto_hide_reset


class CopyToClipboardButton(ToolbarButton):
    label = 'Copy to the clipboard'
    image = 'edit-copy'

    def perform(self, event):
        plot_component = self.container.component

        # We need to hide the toolbar, then put it back after the
        # plot has been saved
        auto_hide_reset = plot_component.auto_hide
        plot_component.auto_hide = True

        width, height = plot_component.outer_bounds

        gc = PlotGraphicsContext((width, height), dpi=72)
        gc.render_component(plot_component)

        bitmap = wx.BitmapFromBufferRGBA(width+1, height+1, gc.bmp_array.flatten())
        data = wx.BitmapDataObject()
        data.SetBitmap(bitmap)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Unable to open the clipboard.", "Error")

        plot_component.auto_hide = auto_hide_reset
