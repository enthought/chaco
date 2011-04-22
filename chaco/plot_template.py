"""
Defines classes needed to support templates in Chaco.

* AbstractTemplatizer
* CodeMetadata
* CodeTemplate
* PlotTemplate
* PlotTemplateException
* TemplateDescriptor
* Templatizable

Also defines the convenience function::

    bind_template(template, vars, type_check=False)

"""


from traits.api import Bool, Dict, HasTraits, Instance, Str



def bind_template(template, vars, type_check=False):
    """
    A convenience method for binding a plot template to set of variables.

    Parameters
    ----------
    template : a list of strings
        The code for the template, or a PlotTemplate object.
    vars : a dict
        Maps a template variable name to an object.
    type_check : Boolean
        If True, raises a PlotTemplateException with the name
        of the variable in *vars* whose type does not match what is
        specified in the template.
    """
    return


class PlotTemplateException(Exception):
    """ Raised for errors in plot templates.
    """
    pass


class TemplateDescriptor(HasTraits):
    """ Describes the names and types of template variables for a template.
    """

    # A dict with the template variable names as keys.  If the template is
    # unbound, the values are string representations of the types of objects
    # expected for each key.  These are simple types, e.g., 'tuple' or
    # 'PlotAxis'. If the template is bound, then the values are object
    # references.
    vars = Dict




class Templatizable(HasTraits):
    """ Mix-in class that makes objects capable of being incorporated
    into a Chaco template.

    Primarily defines the protocol used to query the class for its contents.
    """

    def templatize(self, my_name, ):
        """ Returns a dict mapping the name of the child in the local name space
        to a Templatizable object reference.
        """
        raise NotImplementedError

    def __gettemplate__(self):
        """ Returns a templatized version of the object.
        """

#    def bind(self,

    def rebind(self, obj):
        """ Replaces this object with the state in peer object *obj*.

        This method allows PlotTemplates to be used as live, application-level
        templates and not merely as a means to generating a plot script.

        (If you are having trouble implementing this method for something that
        should be Templatizable, it's probably a sign that you haven't fully
        considered the implications of your design, or that you are doing
        something a little weird.)
        """
        raise NotImplementedError


class PlotTemplate(HasTraits):
    """ Abstract base class for plot templates.
    """
    pass




class AbstractTemplatizer(HasTraits):
    """ A Templatizer accepts any subclass of Templatizable and returns a
    PlotTemplate.
    """



class CodeMetadata(HasTraits):
    """ Represents all the metadata about a plot template, to be stored into
    the generated code.

    The generated code for a plot template must create one of these objects,
    which is then used to drive the loading of the rest of the template.
    """
    # Not used for now, but could be handled later.
    version = "1.0"

    # The name of the Chaco package.
    pkg_name = "enthought.chaco"

    # A dict with the template variable names as keys.  If the template is
    # unbound, the values are string representations of the types of objects
    # expected for each key. These are simple types, e.g., 'tuple' or 'PlotAxis'.
    # If the template is bound, then the values are object references.
    template_vars = Dict

    # The name to evaluate to get the root object when the template
    # is instantiated.  Defaults to "ROOT_OBJ", but you can customize
    # this for aesthetic or readability reasons.
    root_name = Str

class CodeTemplate(PlotTemplate):
    """ A Chaco plot template.

    Because Chaco plot templates are just executable code that produces Chaco
    plots, the PlotTemplate class is used to manage, interact with, and inspect
    the code for the template.
    """

    #-------------------------------------------------------------------------
    # Configuration and general state of the template
    #-------------------------------------------------------------------------

    # Is the template completely bound?
    is_bound = Bool(False)


    #-------------------------------------------------------------------------
    # Object graph traits
    #-------------------------------------------------------------------------

    # The top-level Templatizable component in the plot.
    root = Instance(Templatizable)

    #-------------------------------------------------------------------------
    # Code-related traits
    # These are used during the actual code generation process.
    #-------------------------------------------------------------------------

    # Global variables used during the code generation process.
    code_globals = Dict
    # Imports used during the code generation process.
    code_imports = Dict

    def create_strings(self):
        """ Returns a list of strings which can be passed to bind_template().
        """
        # TODO:  do we need this?? can we do live generation?!!!
        pass

    def load_from_strings(self, stringlist):
        """ Fills this plot template with the template in *stringlist*.

        NOTE: Don't use this to bind a template to data!  There is a much easier
        way to do that: use the bind_template() function.
        """
        pass

    #-------------------------------------------------------------------------
    # Private methods
    #-------------------------------------------------------------------------

    def _write_metadata(self):
        """
        Produces a list of strings representing the code to create the
        metadata portion of this PlotTemplate.
        """
        pass

    #-------------------------------------------------------------------------
    # Methods used by Templatizable objects to query the generator about the
    # state of code generation.
    #-------------------------------------------------------------------------

    def create_global(self, name_hint):
        """ Requests that a new global symbol be allocated with the given name.

        Returns the actual name that was created.
        """
        pass

    def create_import(self, import_line, ):
        """ Adds another import line, verbatim, to the top of the output code.

        No order of imports is guaranteed.
        """
        pass

    def create_template_var(self, name_hint):
        """ Creates a new variable for parameterizing the template.

        Returns a string that represents the special token to be used in the
        output code to signal where the template value can be bound.
        """
        pass

    def create_function(self, name_hint):
        """ Requests that a new function be allocated with the given name.

        Returns the actual name that was created.
        """
        pass


# EOF
