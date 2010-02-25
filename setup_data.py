
# Function to convert simple ETS project names and versions to a requirements
# spec that works for both development builds and stable builds.  Allows
# a caller to specify a max version, which is intended to work along with
# Enthought's standard versioning scheme -- see the following write up:
#    https://svn.enthought.com/enthought/wiki/EnthoughtVersionNumbers
def etsdep(p, min, max=None, literal=False):
    require = '%s >=%s.dev' % (p, min)
    if max is not None:
        if literal is False:
            require = '%s, <%s.a' % (require, max)
        else:
            require = '%s, <%s' % (require, max)
    return require


# Declare our ETS project dependencies.
ENABLE_TRAITS = etsdep('Enable[traits]', '3.3.0')
ENTHOUGHTBASE = etsdep('EnthoughtBase', '3.0.4')
#TRAITSBACKENDQT -- not needed due to the way it is used in chaco2_plot_container_editor.py
TRAITSBACKENDWX = etsdep('TraitsBackendWX', '3.3.0')  # used by chaco_plot_editor.py
TRAITS_UI = etsdep('Traits[ui]', '3.3.0')


INFO = {
    "extras_require": {
        'wx': [
            TRAITSBACKENDWX,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            'numpy >= 1.1.0',
            #'PyQt4', -- not really required by everyone.
            #'wxPython', -- not really required by everyone.
            ],
        },
    "install_requires": [
        ENABLE_TRAITS,
        ENTHOUGHTBASE,
        TRAITS_UI,
        ],
    "name": 'Chaco',
    "version": '3.3.0',
    }

