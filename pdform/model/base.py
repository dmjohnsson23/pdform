from pdfrw import PdfArray, PdfDict
from typing import Union
from weakref import WeakValueDictionary

class Wrapper:
    """
    Base class for all the wrappers in this library, designed to wrap a PdfArray or PdfDict.
    """
    _instances = WeakValueDictionary()
    raw:Union[PdfDict,PdfArray]
    pdf:PdfDict
    def __new__(cls, pdf, raw:Union[PdfDict,PdfArray], *args, **kwargs):
        addr = id(raw)
        instance = cls._instances.get(addr)
        if instance is None:
            instance = super().__new__(cls)
            instance.pdf = pdf
            instance.raw = raw
            cls._instances[addr] = instance
        return instance


class WrappedProperty:
    """
    This is a special type of property designed to work in conjunction with the ``Wrapper`` class to automatically wrap values from ``raw``.
    """
    def __init__(self, key, wrapper, default=None, inheritable=False):
        self.default = default
        self.key = key
        self.wrapper = wrapper
        self.inheritable = inheritable
    def __get__(self, instance:Wrapper, owner):
        if self.inheritable:
            raw = instance.raw.inheritable
        else:
            raw = instance.raw
        try:
            to_wrap = raw[self.key]
        except KeyError:
            return self.default
        if isinstance(self.wrapper, Wrapper):
            return self.wrapper(to_wrap)
        else:
            return self.wrapper(to_wrap)
    def __set__(self, instance:Wrapper, value):
        if self.inheritable:
            raw = instance.raw.inheritable
        else:
            raw = instance.raw
        if isinstance(self.wrapper, Wrapper):
            raw[self.key] = value.raw
        else:
            raw[self.key] = value
    def __delete__(self, instance):
        try:
            del instance.raw[self.key]
        except KeyError:
            pass