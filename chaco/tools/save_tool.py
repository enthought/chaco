""" Defines the SaveTool class.
"""

# Major library imports
import os.path

# Enthought library imports
from traits.api import Enum, Str, Tuple
from enable.api import BaseTool


class SaveTool(BaseTool):
    """ This tool allows the user to press Ctrl+S to save a snapshot image of
    the plot component.
    """

    #: The file that the image is saved in.  The format will be deduced from
    #: the extension.
    filename = Str("saved_plot.png")

    #:-------------------------------------------------------------------------
    #: PDF format options
    #: This mirror the traits in PdfPlotGraphicsContext.
    #:-------------------------------------------------------------------------

    pagesize = Enum("letter", "A4")
    dest_box = Tuple((0.5, 0.5, -0.5, -0.5))
    dest_box_units = Enum("inch", "cm", "mm", "pica")

    #-------------------------------------------------------------------------
    # Override default trait values inherited from BaseTool
    #-------------------------------------------------------------------------

    #: This tool does not have a visual representation (overrides BaseTool).
    draw_mode = "none"

    #: This tool is not visible (overrides BaseTool).
    visible = False

    def normal_key_pressed(self, event):
        """ Handles a key-press when the tool is in the 'normal' state.

        Saves an image of the plot if the keys pressed are Control and S.
        """
        if self.component is None:
            return

        if event.character == "s" and event.control_down:
            if os.path.splitext(self.filename)[-1] == ".pdf":
                self._save_pdf()
            else:
                self._save_raster()
            event.handled = True
        return

    def _save_raster(self):
        """ Saves an image of the component.
        """
        from chaco.plot_graphics_context import PlotGraphicsContext
        gc = PlotGraphicsContext((int(self.component.outer_width), int(self.component.outer_height)))
        self.component.draw(gc, mode="normal")
        gc.save(self.filename)
        return

    def _save_pdf(self):
        from chaco.pdf_graphics_context import PdfPlotGraphicsContext
        gc = PdfPlotGraphicsContext(filename=self.filename,
                pagesize = self.pagesize,
                dest_box = self.dest_box,
                dest_box_units = self.dest_box_units)
        gc.render_component(self.component)
        gc.save()

# EOF
