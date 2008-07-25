#!/usr/bin/env python

# Helper script to make it easier to maintain the tests run by
# $ python setup.py test
#
# Run this script when changing the entries of tests at the end of 
# setup.cfg.  This script will only change the line
#   tests = ....
# in setup.cfg.

tests = []

for line in open('setup.cfg'):
    if line.startswith('# test '):
        tests.append(line[6:].strip())

out = []

for line in open('setup.cfg'):
    if line.startswith('tests ='):
        out.append('tests = %s\n' % ','.join(tests))
    else:
        out.append(line)


fo = open('setup.cfg', 'w')
fo.write(''.join(out))
fo.close()
