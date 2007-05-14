
# Enthought package imports
from enthought.traits.api import Event, HasTraits, Instance, List, Str, This, Trait

# Local relative imports
from stylesheets import Style, StyleSheet


class Stylable(HasTraits):
    """
    A mix-in class to give objects the ability to participate in Chaco's Style
    system.  
    
    The primary functions of the Stylable mix-in class is it:
        1. provide a mechanism for style lookup on parents
        2. cache styles information (automatically invalidated when the stylesheet changes)
        3. allow for objects to only 
    """

    # The parent stylable, or None
    style_parent = Trait(None, None, This)

    # The stylesheet that this component is using
    stylesheet = Instance(StyleSheet, args=())
    
    # The style for this component
    style = Instance(Style, args=())

    # The ID of this stylable object; this ID should be unique across the entire
    # style hierarchy.
    style_id = Str
    
    # The class name of this stylable object, e.g. axis, grid, box, text, etc.
    # This is defined at the class level and defaults to "component".
    style_class = "component"

    # This event is fired when our style changes, or when any of our ancestors'
    # styles change.
    style_updated = Event
    
    #------------------------------------------------------------------------
    # Protected traits
    #------------------------------------------------------------------------
    
    # The cached Style object from our previous query to the stylesheet.  Also
    # includes the parent's stylesheet merged in.  Local changes made to our
    # Style dict are not committed.
    cached_style = Instance(Style, args=())

    cached_ancestors = List

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def save_style(self, style_id=None, as_class=False):
        """
        Saves our style to the stylesheet, using style_id as the identifier
        (or self.style_id if one is not provided).  Alternatively, if as_class
        is True, then saves to the stylesheet using self.style_class.
        """
        pass

    def _cache_style_ancestors(self):
        if self.style_parent is not None:
            self.cached_ancestors = [self.style_parent] + self.style_parent.cached_ancestors
        else:
            self.cached_ancestors = []
        #print "updated ancestors for", self.name + ":", [a.name for a in self.cached_ancestors]
        return

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _style_parent_changed(self, old, new):
        self._cache_style_ancestors()
        
        # Re-wire the event handlers
        if old is not None:
            old.on_trait_event(self._parent_style_updated, "style_updated", remove=True)
        if new is not None:
            new.on_trait_event(self._parent_style_updated, "style_updated")
        
        # We have to do the same thing as if the parent style_updated had fired
        self._parent_style_updated()
        return

    def _stylesheet_changed(self, old, new):
        self.cached_style = self.stylesheet.query(self, self.cached_ancestors)
        self.style_updated = True
        return

    def _parent_style_updated(self):
        if self.style_parent is not None:
            self.set(stylesheet=self.style_parent.stylesheet, trait_change_notify=False)
            self.cached_style = Style(self.style_parent.cached_style)
            self.cached_style.update(self.stylesheet.query(self, self.cached_ancestors))
            print "cached style:", self.cached_style
        else:
            self.cached_style = self.stylesheet.query(self, self.cached_ancestors)
        self.style.set_dict(self.cached_style)
        
        # Now that we have a valid, updated style, fire the event handler to
        # notify our children.
        self.style_updated = True
        return

    #------------------------------------------------------------------------
    # Persistence etc.
    #------------------------------------------------------------------------

    # TODO: add stuff here!



# EOF
