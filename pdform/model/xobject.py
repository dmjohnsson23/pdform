from .base import Wrapper
from .rect import Rect
from .content_stream import ContentStream
from pdfrw import PdfDict, PdfName, PdfString
import re
from typing import Union

class FormXObject(Wrapper):
    raw: PdfDict
    @classmethod
    def new(cls, bbox:Rect, stream:Union[str,ContentStream], resources:PdfDict=None):
        xobject = PdfDict(
            Type = 'XObject',
            Subtype = 'Form',
            FormType = 1,
            BBox = bbox,
            Resources = resources if resources is not None else PdfDict()
        )
        xobject.stream = str(stream)
        return cls(xobject)
