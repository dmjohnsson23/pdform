from .base import Wrapper
from .rect import Rect
from .content_stream import ContentStream
from pikepdf import Dictionary, Array, Stream
from typing import Union

class FormXObject(Wrapper):
    raw: Dictionary
    @classmethod
    def new(cls, pdf, bbox:Union[Rect,Array], stream:Union[bytes,ContentStream], resources:Dictionary=None):
        if isinstance(bbox, Rect):
            bbox = bbox.raw
        xobject = Stream(pdf, bytes(stream), 
            Type = 'XObject',
            Subtype = 'Form',
            FormType = 1,
            BBox = bbox,
            Resources = resources if resources is not None else Dictionary()
        )
        return cls(pdf, xobject)

# TODO ImageXObject, base XObject