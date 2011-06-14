#! /bin/env python

# Standard library imports
import os.path
import wave
import numpy

# Enthought library imports
from traits.util.resource import find_resource

def wav_to_numeric( fname, max_frames=-1 ):
  f = wave.open( fname, 'rb' )
  sampleRate = f.getframerate()
  channels = f.getnchannels()

  if max_frames < 0:
      max_frames = f.getnframes()

  frames = f.readframes(max_frames)

  if f.getsampwidth() == 2:
      data = numpy.fromstring(frames, numpy.uint16).astype(numpy.float64) - (2**15 - 0.5)
  else:
      data = numpy.fromstring(frames, numpy.uint8).astype(numpy.float64) - 127.5

  if channels == 2:
      left = data[0::2]
      right = data[1::2]

      data = left

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

