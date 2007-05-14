"""
Defines the classes needed to support templates in Chaco:
    PlotTemplateException
    TemplateMetadata
    Templatizable
    PlotTemplate

Also defines the convenience function:
    bind_template(template, vars, type_check=False)

A PlotTemplate consists of a TemplateDescriptor

"""


from enthought.traits.api import Dict, false, HasTraits, Instance, Str



def bind_template(template, vars, type_check=False):
    """
    A convenience method for binding a plot template to set of variables.
        template: a list of strings representing the code for the template, or 
                  a PlotTemplate object
        vars: a dict mapping a template variable name to an object
        type_check: if True, raises a PlotTemplateException with the name
                    of the variable in vars whose type does not match what is
                    specified in the template
    """
    return


class PlotTemplateException(Exception):
    pass


class TemplateDescriptor(HasTraits):
    """
    Describes the names and types of template variables for a template.
    """

    # A dict with the template variable names as keys.  If the template is
    # unbound, the values are string representations of the types of objects
    # expected for each key.  These are simple types, e.g. 'tuple' or 'PlotAxis'.
    # If the template is bound, then the values are object references.
    vars = Dict




class Templatizable(HasTraits):
    """
    Mix-in class for objects that want to be capable of being incorporated
    into a Chaco template using a TemplateGenerator.  Primarily defines the
    protocol that the TemplateGenerator uses to query the class for its
    contents.
    """

    def templatize(self, my_name, ):
        """
        Returns a dict mapping the name of the child in our local namespace
        to a Templatizable object reference.
        """
        raise NotImplementedError
    
    def __gettemplate__(self):
        """
        Returns a templatized version of the object
        """
    
#    def bind(self, 
    
    def rebind(self, obj):
        """
        Replaces this object with the state in peer object 'obj'.  This method
        allows PlotTemplates to be used as live, application-level templates
        and not merely as a means to generating a plot script.
        
        (If you are having trouble implementing this method for something that
        should be Templatizable, it's probably a sign that you haven't fully
        though your design through, or that you are doing something a little
        wonky.)
        """
        raise NotImplementedError
    

class PlotTemplate(HasTraits):
    pass




class AbstractTemplatizer(HasTraits):
    """
    A Templatizer accepts any subclass of Templatizable and returns a PlotTemplate.
    Different templatizers will create a 
    """



class CodeMetadata(HasTraits):
    """
    Represents all the metadata about a plot template that will be stored into
    the generated code.  The generated code for a plot template must create one
    of these objects, which is then used to drive the loading of the rest of the
    template.
    """
    # Not used for now, but could be handle later
    version = "1.0"
    
    # The name of the chaco package
    pkg_name = "enthought.chaco2"
    
    # A dict with the template variable names as keys.  If the template is
    # unbound, the values are string representations of the types of objects
    # expected for each key.  These are simple types, e.g. 'tuple' or 'PlotAxis'.
    # If the template is bound, then the values are object references.
    template_vars = Dict

    # The name that will be evaluated to get the root object when the template
    # is instantiated.  Defaults to "ROOT_OBJ", but users may want to customize
    # this for aesthetic/readability reasons.
    root_name = Str

class CodeTemplate(PlotTemplate):
    """
    A Chaco template 
    Since Chaco plot templates are just executable code that produces Chaco
    plots, the PlotTemplate class is used to manage, interact with, and inspect
    the code for the template.
    """
    
    #-------------------------------------------------------------------------
    # Configuration and general state of the template
    #-------------------------------------------------------------------------

    # Is the template completely bound?
    is_bound = false
    
    
    #-------------------------------------------------------------------------
    # Object graph traits
    #-------------------------------------------------------------------------
    
    # The top-level Templatizable component in the plot
    root = Instance(Templatizable)
    
    #-------------------------------------------------------------------------
    # Code-related traits
    # These are used during the actual code generation process.  They are
    # exposed as public traits so that objects can 
    #-------------------------------------------------------------------------
    
    code_globals = Dict
    
    code_imports = Dict

    def create_strings(self):
        """
        Returns a list of strings which, when passed to bind_template() with
        the proper 
        """
        # TODO:  do we need this?? can we do live generation?!!!
        pass

    def load_from_strings(self, stringlist):
        """
        Fills this PlotTemplate with the template in stringlist.  Allows the
        PlotTemplate to be 
        
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
        """
        Requests that a new global symbol be allocated with the given name.
        Returns the actual name that was created.
        """
        pass
    
    def create_import(self, import_line, ):
        """
        Adds another import line, verbatim, to the top of output_code.  No order
        is guaranteed
        """
        pass
    
    def create_template_var(self, name_hint):
        """
        Creates a new variable for parameterizing the template.  Returns a
        string that represents the special token that should be used in the
        output_code to signal where the template value should be bound.
        """
        pass
    
    def create_function(self, name_hint):
        """
        Requests that a new function be allocated with the given name.
        Returns the actual name that was created.
        """
        pass


# EOF
