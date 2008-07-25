# 
# Sample Chaco2 template
# 
# Chaco templates are just python modules.  They generally consist of a series
# of top-level functions, each of which build out a plot component in the
# plot hierarchy.
#
# They must define a special symbol __plot_metadata__ which is an instance of
# TemplateMetadata.


from enthought.chaco2.api import TemplateMetadata

__plot_metadata__ = TemplateMetadata(version = "1.0",
    pkg_name = "enthought.chaco2",
    root_name = "top_frame",
    template_vars = { "left_slot": "VPlotContainer",
        "center_slot": "OverlayPlotContainer",
        "bottom_data": "ArrayDataSource" }
    )


