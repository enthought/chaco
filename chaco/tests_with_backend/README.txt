
More unit tests for Chaco
=========================
These tests require an installed backend for traitsui such as PyQt or wx. 
They are separated so that TravisCI test-running can be done on different 
folders for the different versions of python because it is tricky to 
install PyQt on the Python 2.6 virtualenv.