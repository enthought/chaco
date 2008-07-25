"""
Defines mask-type filters.
"""

from filters import AbstractFilter

class AbstractMaskFilter(AbstractFilter):
    pass
    
class MaskFilter(AbstractMaskFilter):
    pass
    
class ImageMaskFilter(AbstractMaskFilter):
    pass

# EOF
