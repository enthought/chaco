

# Major library imports
import warnings

# PDF imports from reportlab
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm, mm, pica
from enthought.kiva.backend_pdf import GraphicsContext

PAGE_SIZE_MAP = {
        "letter": letter,
        "A4": A4,
        }

UNITS_MAP = {
        "inch": inch,
        "cm": cm,
        "mm": mm,
        "pica": pica,
        }


class PdfPlotGraphicsContext(GraphicsContext):
    """ A convenience class for rendering PlotComponents onto PDF
    """

    # The name of the file that this graphics context will use when
    # gc.save() is called without a filename being supplied.
    filename = "saved_plot.pdf"

    # The page size of the generated PDF
    pagesize = "letter"  # Enum("letter", "A4")

    # A tuple (x, y, width, height) specifying the box into which the plot
    # should be rendered.  **x** and **y** correspond to the lower-left hand
    # coordinates of the box in the coordinates of the page (i.e. 0,0 is at the
    # lower left).  **width** and **height** can be positive or negative;
    # if they are positive, they are interpreted as distances from (x,y);
    # if they are negative, they are interpreted as distances from the right
    # and top of the page, respectively.
    dest_box = (0.5, 0.5, -0.5, -0.5)

    # The units of the values in dest_box
    dest_box_units = "inch"   # Enum("inch", "cm", "mm", "pica")


    def __init__(self, pdf_canvas=None, filename=None, pagesize=None,
                 dest_box=None, dest_box_units=None):
        if filename:
            self.filename = filename
        if pagesize:
            self.pagesize = pagesize
        if dest_box:
            self.dest_box = dest_box
        if dest_box_units:
            self.dest_box_units = dest_box_units
        
        if pdf_canvas == None:
            pdf_canvas = self._create_new_canvas()
        
        GraphicsContext.__init__(self, pdf_canvas)


    def render_component(self, component, container_coords=False,
                         halign="center", valign="top"):
        """ Erases the current contents of the graphics context and renders the
        given component at the maximum possible scaling while preserving aspect
        ratio.
        
        Parameters
        ----------
        component : Component
            The component to be rendered.
        container_coords : Boolean
            Whether to use coordinates of the component's container
        halign : "center", "left", "right"
            Determines the position of the component if it is narrower than the
            graphics context area (after scaling)
        valign : "center", "top", "bottom"
            Determiens the position of the component if it is shorter than the
            graphics context area (after scaling)
            
        Description 
        -----------
        If *container_coords* is False, then the (0,0) coordinate of this 
        graphics context corresponds to the lower-left corner of the 
        component's **outer_bounds**. If *container_coords* is True, then the
        method draws the component as it appears inside its container, i.e., it
        treats (0,0) of the graphics context as the lower-left corner of the
        container's outer bounds.
        """
        
        x, y = component.outer_position
        if container_coords:
            width, height = component.container.bounds
        else:
            x = -x
            y = -y
            width, height = component.outer_bounds

        # Compute the correct scaling to fit the component into the available
        # canvas space while preserving aspect ratio.
        units = UNITS_MAP[self.dest_box_units]
        pagesize = PAGE_SIZE_MAP[self.pagesize]

        full_page_width = pagesize[0]
        full_page_height = pagesize[1]
        page_offset_x = self.dest_box[0] * units
        page_offset_y = self.dest_box[1] * units
        page_width = self.dest_box[2] * units
        page_height = self.dest_box[3] * units

        if page_width < 0:
            page_width += full_page_width - page_offset_x
        if page_height < 0:
            page_height += full_page_height - page_offset_y
        
        aspect = float(width) / float(height)

        if aspect >= page_width / page_height:
            # We are limited in width, so use widths to compute the scale
            # factor between pixels to page units.  (We want square pixels,
            # so we re-use this scale for the vertical dimension.)
            scale = float(page_width) / float(width)
            trans_width = page_width

            trans_height = height * scale
            trans_x = x * scale
            trans_y = y * scale
            if valign == "top":
                trans_y += page_height - trans_height
            elif valign == "center":
                trans_y += (page_height - trans_height) / 2.0
            
        else:
            # We are limited in height
            scale = page_height / height
            trans_height = page_height

            trans_width = width * scale
            trans_x = x * scale
            trans_y = y * scale
            if halign == "right":
                trans_x += page_width - trans_width
            elif halign == "center":
                trans_x += (page_width - trans_width) / 2.0

        self.translate_ctm(trans_x, trans_y)
        self.scale_ctm(scale, scale)
        self.clip_to_rect(0, 0, trans_width, trans_height)
        old_bb_setting = component.use_backbuffer
        component.use_backbuffer = False
        component.draw(self, view_bounds=(0, 0, trans_width, trans_height))
        component.use_backbuffer = old_bb_setting
        return

    def save(self, filename=None):
        self.gc.save()

    def _create_new_canvas(self):
        pagesize = PAGE_SIZE_MAP[self.pagesize]
        units = UNITS_MAP[self.dest_box_units]
        gc = Canvas(filename=self.filename, pagesize=pagesize)

        width = pagesize[0] * units * inch / 72.0
        height = pagesize[1] * units * inch / 72.0
        x = self.dest_box[0] * units
        y = self.dest_box[1] * units
        w = self.dest_box[2] * units
        h = self.dest_box[3] * units

        if w < 0:
            w += width
        if h < 0:
            h += height

        if w < 0 or h < 0:
            warnings.warn("Margins exceed page dimensions.")
            self.gc = None
            return

        gc.translate(x,y)
        path = gc.beginPath()
        path.rect(0, 0, w, h)
        gc.clipPath(path, stroke=0, fill=0)
        return gc

