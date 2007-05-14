
from enthought.traits.api import Enum, HasTraits, Int, Str


class Preferences(HasTraits):
    """
    Contains all the preferences that configure the chaco shell session.
    """
    
    window_width = Int(600)
    window_height = Int(600)
    plot_type = Enum("line", "scatter")
    default_window_name = Str("Chaco Plot")

    @classmethod
    def from_file(self, filename):
        """
        Creates a new preferences object from a file on disk
        """
        pass


    def load(self, filename):
        """
        Loads preferences file; existing settings will be overwritten
        """
        pass


    def save(self, filename):
        """ Saves the preferences to file """
        pass


# EOF
