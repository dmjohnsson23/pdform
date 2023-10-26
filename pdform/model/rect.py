from pikepdf import Array, Rectangle
from .base import Wrapper, WrappedProperty


class Rect(Wrapper):
    """
    Represents a rectangle in the PDF. Used for bounding boxes, media boxes, and so forth.
    """
    raw:Array
    @property
    def helper(self):
        """
        The rectangle as a pikepdf.Rectangle helper object
        """
        return Rectangle(self.raw)
    @helper.setter
    def helper(self, value:Rectangle):
        self.raw = value.as_array()
        
    # Note: The PDF standard defines the origin as the bottom-left corner of the page (See 8.3.2.3)
    # Points are defined as [lower_left_x, lower_left_y, upper_right_x, upper_right_y] (See 4.40)
    @classmethod
    def new(cls, pdf, left:float, bottom:float, right:float, top:float):
        return cls(pdf, Array([float(left), float(bottom), float(right), float(top)]))
    
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
        return Rect.new(self.pdf, 0, 0, self.width, self.height)