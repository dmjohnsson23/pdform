from .base import Wrapper
from .rect import Rect
from .content_stream import ContentStream
from pdfrw import PdfDict, PdfName, PdfString, PdfArray
import re
from typing import Union

class FormXObject(Wrapper):
    raw: PdfDict
    @classmethod
    def new(cls, pdf, bbox:Union[Rect,PdfArray], stream:Union[str,ContentStream], resources:PdfDict=None):
        if isinstance(bbox, Rect):
            bbox = bbox.raw
        xobject = PdfDict(
            Type = 'XObject',
            Subtype = 'Form',
            FormType = 1,
            BBox = bbox,
            Resources = resources if resources is not None else PdfDict()
        )
        xobject.stream = str(stream)
        return cls(pdf, xobject)
