import os.path
import xml.etree.cElementTree as etree

from enthought.chaco.api import AbstractOverlay
from enthought.pyface.timer.timer import Timer
from enthought.traits.api import Instance, Str, Enum, Float, Int
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

    # The position of the legend with respect to its overlaid component.
    #
    # * c  = Center
    # * ur = Upper Right
    # * ul = Upper Left
    # * ll = Lower Left
    # * lr = Lower Right
    align = Enum("c", "ur", "ul", "ll", "lr")

    # How big should the graphic be in comparison to the rest of the plot
    # area
    scale_factor = Float(0.5)

    # Initial transparency
    alpha = Float(1.0)

    # The minimum time it takes for the the layer to fade out, in
    # milliseconds. Actual time may be longer, depending on the pyface toolkit
    fade_out_time = Float(50)

    # The number of steps to take to fade from the initial transparency to
    # invisible
    fade_out_steps = Int(10)

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

        plot_width = self.component.width
        plot_height = self.component.height

        origin_x = self.component.padding_left
        origin_y = self.component.padding_top

        # zoom percentage, use the scale_factor as a % of the plot size.
        # base the size on the smaller aspect - if the plot is tall and narrow
        # the overlay should be 50% of the width, if the plot is short and wide
        # the overlay should be 50% of the height.
        if gc.height() < gc.width():
            scale = (plot_height/self.doc_height)*self.scale_factor
        else:
            scale = (plot_width/self.doc_width)*self.scale_factor

        scale_width = scale*self.doc_width
        scale_height = scale*self.doc_height

        # Set up the transforms to align the graphic to the desired
        # position keeping in mind the SVG origin is the upper right
        # with y positive down
        if self.align == 'ur':
            gc.translate_ctm(origin_x + (plot_width-scale_width),
                            origin_y + plot_height)
        elif self.align == 'lr':
            gc.translate_ctm(origin_x + (plot_width-scale_width),
                            origin_y + scale_height)
        elif self.align == 'ul':
            gc.translate_ctm(origin_x,
                            origin_y + plot_height)
        elif self.align == 'll':
            gc.translate_ctm(origin_x,
                            origin_y + scale_height)
        else:
            gc.translate_ctm(origin_x + (plot_width-scale_width)/2,
                             origin_y + (plot_height+scale_height)/2)


        gc.scale_ctm(scale, -scale)

        self.document.render(gc)

        self._draw_component(gc, view_bounds, mode)
        gc.restore_state()

        return

    def fade_out(self):
        interval = self.fade_out_time/self.fade_out_steps
        self.timer = Timer(interval, self._fade_out_step)

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
