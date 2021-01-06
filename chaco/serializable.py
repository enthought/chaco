""" Defines the Serializable mix-in class.
"""




class Serializable(object):
    """
    Mix-in class to help serialization.  Serializes just the attributes in
    **_pickles**.

    This mix-in works best when all the classes in a hierarchy subclass
    from it.  It solves the problem of allowing each class to specify
    its own set of attributes to pickle and attributes to ignore, without
    having to also implement __getstate__ and __setstate__.
    """

    # The basic list of attributes to save.  These get set without firing
    # any trait events.
    _pickles = None

    # A list of the parents of this class that will be searched for their
    # list of _pickles.  Only the parents in this list that inherit from
    # Serialized will be pickled.  The process stops at the first item in
    # __pickle_parents that is not a subclass of Serialized.
    #
    # This is a double-underscore variable so that Python's attribute name
    # will shield base class
#    __pickle_parents = None

    def _get_pickle_parents(self):
        """
        Subclasses can override this method to return the list of base
        classes they want to have the serializer look at.
        """
        bases = []
        for cls in self.__class__.__mro__:
            if cls is Serializable:
                # don't add Serializable to the list of parents
                continue
            elif issubclass(cls, Serializable):
                bases.append(cls)
            else:
                break
        return bases

    def _pre_save(self):
        """
        Called before __getstate__ to give the object a chance to tidy up
        and get ready to be saved.  This usually also calls the superclass.
        """
        return

    def _post_load(self):
        """
        Called after __setstate__ finishes restoring the state on the object.
        This method usually needs to include a call to super(cls, self)._post_load().
        Avoid explicitly calling a parent class by name, because in general
        you want post_load() to happen in the same order as MRO, which super()
        does automatically.
        """
        print('Serializable._post_load')
        pass

    def _do_setstate(self, state):
        """
        Called by __setstate__ to allow the subclass to set its state in a
        special way.

        Subclasses should override this instead of Serializable.__setstate__
        because we need Serializable's implementation to call _post_load() after
        all the _do_setstate() have returned.)
        """
        # Quietly set all the attributes
        self.trait_setq(**state)
        return

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

#    def __getstate__(self):
#        #idstring = self.__class__.__name__ + " id=" + str(id(self))
#        # Give the object a chance to tidy up before saving
#        self._pre_save()
#
#        # Get the attributes that this class needs to serialize.  We do this by
#        # marching up the list of parent classes in _pickle_parents and getting
#        # their lists of _pickles.
#        all_pickles = Set()
#        pickle_parents = self._get_pickle_parents()
#        for parent_class in pickle_parents:
#            all_pickles.update(parent_class._pickles)
#
#        if self._pickles is not None:
#            all_pickles.update(self._pickles)
#
#        state = {}
#        for attrib in all_pickles:
#            state[attrib] = getattr(self, attrib)
#
#        print('<<<<<<<<<<<<<', self)
#        for key,value in state.items():
#            print(key, type(value))
#        print '>>>>>>>>>>>>>'
#
#        return state

    #~ def __setstate__(self, state):
        #~ idstring = self.__class__.__name__ + " id=" + str(id(self))
        #~ self._do_setstate(state)
        #~ self._post_load()
        #~ return


# EOF
