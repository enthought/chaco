""" Defines the Preferences class for the Chaco shell.
"""

from enable.api import white_color_trait
from traits.api import Enum, HasTraits, Int, Str


class Preferences(HasTraits):
    """Contains all the preferences that configure the Chaco shell session."""

    # Width of the plot window, in pixels.
    window_width = Int(600)

    # Height of the plot window, in pixels.
    window_height = Int(600)

    # The type of plot to display.
    plot_type = Enum("line", "scatter")

    # Default name to use for the plot window.
    default_window_name = Str("Chaco Plot")

    # The default background color.
    bgcolor = white_color_trait

    # The default location of the origin for new image plots
    image_default_origin = Enum(
        "top left", "bottom left", "bottom right", "top right"
    )

    @classmethod
    def from_file(cls, filename):
        """Creates a new preferences object from a file on disk."""
        prefs = cls()
        prefs.load(filename)
        return prefs

    def load(self, filename):
        """Loads a preferences file; existing settings are overwritten."""
        pass

    def save(self, filename):
        """Saves the preferences to *filename*."""
        pass
