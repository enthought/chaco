
from enthought.kiva.backend_image import GraphicsContext
from enthought.traits.api import Str

from enthought.chaco2.api import BaseTool

class SaveTool(BaseTool):
    """
    This tool allows the user to press Ctrl+S to do a snapshot of the plot
    component.
    """
    
    filename = Str("saved_plot.png")
    
    draw_mode = "none"
    visible = False
    
    def normal_key_pressed(self, event):
        if event.character == "s" and event.control_down:
            self._save_component()
            event.handled = True
        return
    
    def _save_component(self):
        if self.component is not None:
            gc = GraphicsContext((int(self.component.width), int(self.component.height)))
            self.component.draw(gc, mode="normal")
            gc.save(self.filename)
        return


# EOF
