#!/usr/bin/env python

from traits.api import HasTraits, Int

class Boo( HasTraits ):
  print( 'start Boo')
  a = Int(5)
  b = 12
  print( type(a) )
  print (type(b) )
  print( 'end Boo')

  def __init__(self):
    print( '__init__' )

  foo = 4

boo = Boo()
print( boo.a )
print( boo.b )
print( type(boo.a) )
print (type(boo.b) )


