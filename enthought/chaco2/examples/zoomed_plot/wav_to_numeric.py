#! /bin/env python
import wave
from enthought.util.numerix import arange, fromstring, UInt8, Float64

def wav_to_numeric( fname ):
  f= wave.open( fname, 'rb' )
  sampleRate= f.getframerate()
  channels= f.getnchannels()
  
  # get the first million samples...
  s= f.readframes(10000000)
  
  # I think we need to be a little more careful about type here.
  # We also may need to work with byteswap
  data = fromstring(s,UInt8).astype(Float64) - 127.5
  index = arange(len(data)) * 1.0/sampleRate  
  return index, data
  
def test():
    fname = r"C:\Program Files\Windows NT\Pinball\SOUND999.WAV"    
    index, data = wav_to_numeric(fname)
    #print ary[:100]
    return index, data
    
if __name__== '__main__':
    test()

