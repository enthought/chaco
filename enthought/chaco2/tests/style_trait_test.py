

from enthought.traits.api import HasTraits, Dict, Delegate, Instance, Str


#class StyleTrait(TraitHandler):
    #is_mapped = True
    #def __init__(self, name, dict_name='style'):
        #self.name = name
        #self.fast_validate = (6, )

class StyleDict(HasTraits):
    
    style_dict = Dict
    
    def __getattr__(self, name):
        if name.startswith("QQ"):
            return self.style_dict[name[2:]]

    def __setattr__(self, name, val):
        print "name:", name, "val:", val
        if not hasattr(self, name):
            if name.startswith("QQ"):
                print "setting", name[2:], "to", val
                self.style_dict[name[2:]] = val
            else:
                print "bogus name:", name
        else:
            HasTraits.__setattr__(self, name, val)
        return


StyleTrait = Delegate("style", "QQ*", modify=True)

class Foo(HasTraits):
    style = Instance(StyleDict, args=())
    
    color = StyleTrait
    size = StyleTrait
    fuzziness = StyleTrait

#x = Foo()
#x.style.style_dict["color"] = "green"
#print x.color

#print "\nsetting via attribute on Foo:"
#x.color = "black"

#print x.color
#print x.style.style_dict

class Foo(HasTraits):
    
    color 

