import wx

from enthought.enable.tools.toolbars.toolbar_buttons import Button
from enthought.chaco.tools.simple_zoom import SimpleZoom
from enthought.chaco.api import PlotGraphicsContext
from enthought.kiva.backend_image import Image
from enthought.pyface.image_resource import ImageResource
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
        
class GhostButton(ToolbarButton):
    label = 'Create a ghost'
    image = 'ghost'
        
    def perform(self, event):
        self.container.component.ghost_requested = True
        return

class IndexAxisLogButton(ToolbarButton):
    label = 'Change index axis scale'
    image = 'log_x'
        
    def perform(self, event):
        if self.container.component.index_scale == 'linear':
            self.container.component.index_scale = 'log'
        else:
            self.container.component.index_scale = 'linear'
        return
    
class ValueAxisLogButton(ToolbarButton):
    label = 'Change value axis scale'
    image = 'log_y'
        
    def perform(self, event):
        if self.container.component.value_scale == 'linear':
            self.container.component.value_scale = 'log'
        else:
            self.container.component.value_scale = 'linear'
        return

class ZoomResetButton(ToolbarButton):
    label = 'Zoom reset'
    image = 'view_previous'
    
    def perform(self, event):
        plot_component = self.container.component
        
        for overlay in plot_component.overlays:
            if isinstance(overlay, SimpleZoom):
                overlay._reset_state_pressed()
            
             
    
class SaveAsButton(ToolbarButton):
    label = 'Save As'
    image = 'save_as'
    
    file = File()
    
    traits_view = View(Item('file'), width=300, buttons=['OK', 'Cancel'])

    def perform(self, event):
        plot_component = self.container.component
        
        ui = self.edit_traits(kind='modal')
        if not ui.result:
            return

        # We need to hide the toolbar, then put it back after the
        # plot has been saved
        auto_hide_reset = plot_component.auto_hide
        plot_component.auto_hide = True

        width, height = plot_component.outer_bounds
        
        gc = PlotGraphicsContext((width, height), dpi=72)
        gc.render_component(plot_component)
        gc.save(self.file)

class CopyToClipboardButton(ToolbarButton):
    label = 'Copy to the clipboard'
    image = 'clipboard'
        
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
