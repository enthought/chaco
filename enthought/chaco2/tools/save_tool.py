""" Defines the SaveTool class.
"""
from enthought.kiva.backend_image import GraphicsContext
from enthought.traits.api import Str

from enthought.chaco2.api import BaseTool

class SaveTool(BaseTool):
    """ This tool allows the user to press Ctrl+S to save a snapshot image of
    the plot component.
    """
    
    # The file that the image is saved in.
    filename = Str("saved_plot.png")
    
    # This tool does not have a visual representation (overrides BaseTool).
    draw_mode = "none"
    # This tool is not visible (overrides BaseTool).
    visible = False
    
    def normal_key_pressed(self, event):
        """ Handles a key-press when the tool is in the 'normal' state.
        
        Saves an image of the plot if the keys pressed are Control and S.
        """
        if event.character == "s" and event.control_down:
            self._save_component()
            event.handled = True
        return
    
    def _save_component(self):
        """ Saves an image of the component.
        """
        if self.component is not None:
            gc = GraphicsContext((int(self.component.width), int(self.component.height)))
            self.component.draw(gc, mode="normal")
            gc.save(self.filename)
        return


# EOF
