#! /bin/env python
import wave
import numpy

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
    fname = r"C:\Program Files\Windows NT\Pinball\SOUND999.WAV"    
    index, data = wav_to_numeric(fname)
    #print ary[:100]
    return index, data
    
if __name__== '__main__':
    test()

