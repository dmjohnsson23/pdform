from pdfrw import PdfArray
from .base import Wrapper, WrappedProperty
from .rect import Rect


class Rect(Wrapper):
    """
    Represents a rectangle in the PDF. Used for bounding boxes, media boxes, and so forth.
    """
    raw:PdfArray
    # Note: The PDF standard defines the origin as the bottom-left corner of the page (See 8.3.2.3)
    # Points are defined as [lower_left_x, lower_left_y, upper_right_x, upper_right_y] (See 4.40)
    @classmethod
    def new(cls, pdf, left:float, bottom:float, top:float, right:float):
        return cls(pdf, PdfArray([left, bottom, top, right]))
    
    left = WrappedProperty(0, float)
    bottom = WrappedProperty(1, float)
    right = WrappedProperty(2, float)
    top = WrappedProperty(3, float)

    @property
    def height(self)->float:
        return self.top - self.bottom
    @property
    def width(self)->float:
        return self.right - self.left
    
    def to_bbox(self):
        """
        Get a rect with the same width and height as this one, but located at (0, 0).

        Bounding boxes represent independent coordinate systems, such as for form XObjects.
        """
        return Rect.new(0, 0, self.width, self.height)