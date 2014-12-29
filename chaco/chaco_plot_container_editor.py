""" Deprecated alias for ComponentEditor.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import warnings

from enable.component_editor import ComponentEditor


class PlotContainerEditor(ComponentEditor):
    """ Deprecated alias for ComponentEditor.
    """

    def __init__(self, *args, **kwds):
        super(PlotContainerEditor, self).__init__(*args, **kwds)
        warnings.warn("DEPRECATED: Use enable.component_editor"
            ".ComponentEditor instead.", DeprecationWarning)
