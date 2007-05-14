
from enthought.kiva.backend_image import GraphicsContext

class PlotGraphicsContext(GraphicsContext):
    """
    This is a Kiva graphics context to facilitate rendering plots and plot
    components into an offscreen/memory buffer.  Its only real difference
    from a normal Kiva GC is that it correctly offsets the coordinate
    frame by (0.5, 0.5) and increases the actual size of the image by 
    1 pixel in each dimension.  (When rendering into on-screen windows 
    through Enable, this transformation step is handled by Enable.)
    
    FIXME: Right now this does not resize correctly.  (But you shouldn't
    resize your GC, anyway!)
    """
    
    def __init__(self, size_or_ary, *args, **kw):
        if type(size_or_ary) in (list, tuple) and len(size_or_ary) == 2:
            size_or_ary = (size_or_ary[0]+1, size_or_ary[1]+1)
        
        super(PlotGraphicsContext, self).__init__(size_or_ary, *args, **kw)
        self.translate_ctm(0.5, 0.5)
        return

    def render_component(self, component, container_coords=False):
        """
        Renders the given component with (0,0) of this GC corresponding
        to the lower-left corner of the component's outer_bounds.  If
        container_coords is True, then draws the component as it appears
        inside its container, i.e. treat (0,0) of the GC as the lower-left
        corner of the container's outer bounds.
        """
        
        x, y = component.outer_position
        if not container_coords:
            x = -x
            y = -y
        self.translate_ctm(x, y)
        component.draw(self)
        return

    def clip_to_rect(self, x, y, width, height):
        GraphicsContext.clip_to_rect(self, x-0.5, y-0.5, width+1, height+1)

# EOF

