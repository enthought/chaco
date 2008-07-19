#! /bin/env python

# Standard library imports
import os.path
import wave
import numpy

# Enthought library imports
from enthought.util.resource import find_resource

def wav_to_numeric( fname ):
  f = wave.open( fname, 'rb' )
  sampleRate = f.getframerate()
  channels = f.getnchannels()
  
  # get the first million samples...
  s = f.readframes(10000000)
  
  # I think we need to be a little more careful about type here.
  # We also may need to work with byteswap
  data = numpy.fromstring(s, numpy.dtype('uint8')).astype(numpy.float64) - 127.5
  index = numpy.arange(len(data)) * 1.0/sampleRate  
  return index, data
  
def test():
    sample_path = os.path.join('examples','data','sample.wav')
    alt_path = os.path.join('..','data','sample.wav')
    fname = find_resource('Chaco', sample_path, alt_path=alt_path,
        return_path=True)
    index, data = wav_to_numeric(fname)
    print data[:100]
    return index, data
    
if __name__== '__main__':
    test()

