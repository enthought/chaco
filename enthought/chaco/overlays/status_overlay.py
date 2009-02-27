import os.path
import xml.etree.cElementTree as etree

from enthought.chaco.api import AbstractOverlay
from enthought.pyface.timer.timer import Timer
from enthought.traits.api import Instance, Str
from enthought.savage.svg.document import SVGDocument
from enthought.savage.svg.backends.kiva.renderer import Renderer as KivaRenderer

class StatusOverlay(AbstractOverlay):
    
    filename = Str()
    document = Instance(SVGDocument)

    # its possible to get the doc width and height, though the entire
    # image would have to be rendered to a temporary gc or something
    # similar. For now the image size is hard coded
    doc_width = 48.0
    doc_height = 48.0

    alpha = 1.0

    def __init__(self, component, *args, **kw):
        super(StatusOverlay, self).__init__(component, *args, **kw)

        if self.document is None:
            if self.filename == '':
                self.filename = os.path.join(os.path.dirname(__file__), 'data', 
                                            'Dialog-error.svg')
            tree = etree.parse(self.filename)
            root = tree.getroot()
            self.document = SVGDocument(root, renderer=KivaRenderer)
    

    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.
        
        Implements AbstractOverlay.
        """
        gc.save_state()

        gc.set_alpha(self.alpha)

        # zoom percentage, I want it to be 50% of the plot size.
        # base the size on the smaller aspect - if the plot is tall and narrow
        # the overlay should be 50% of the width, if the plot is short and wide
        # the overlay should be 50% of the height.
        if gc.height() < gc.width():
            scale = (gc.height()/self.doc_height)*0.5
        else:
            scale = (gc.width()/self.doc_width)*0.5

        scale_width = scale*self.doc_width
        scale_height = scale*self.doc_height

        # SVG origin is upper right with y positive is down. argh.
        # Set up the transforms to fix this up.
        gc.translate_ctm((gc.width()-scale_width)/2,
                         (gc.height()+scale_height)/2)
        
        gc.scale_ctm(scale, -scale)

        self.document.render(gc)
                
        self._draw_component(gc, view_bounds, mode)
        gc.restore_state()

        return
        
    def fade_out(self):
        self.timer = Timer(0.05, self._fade_out_step)
        
    def _fade_out_step(self):
        """ Fades out the overlay over a half second. then removes it from
            the other_component's overlays
        """
        if self.alpha <= 0:
            self.component.overlays.remove(self)
            self.alpha = 1.0
            raise StopIteration
        else:
            self.alpha -= 0.1
            self.component.request_redraw()
                    
class ErrorOverlay(StatusOverlay):
    filename = os.path.join(os.path.dirname(__file__), 'data', 
                                            'Dialog-error.svg')
                                            
class WarningOverlay(StatusOverlay):
    filename = os.path.join(os.path.dirname(__file__), 'data', 
                                            'Dialog-warning.svg')
