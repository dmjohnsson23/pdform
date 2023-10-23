from pdfrw import PdfArray, PdfDict
from typing import Union, Type
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


class ArrayWrapper(Wrapper):
    raw:PdfArray
    def __init__(self, pdf, raw, contained_type):
        self.contained_type = contained_type
        super().__init__(pdf, raw)
    
    def _wrap(self, value):
        if isinstance(self.contained_type, type) and issubclass(self.contained_type, Wrapper):
            return self.contained_type(self.pdf, value)
        else:
            return self.contained_type(value)
    def _unwrap(self, value):
        if isinstance(value, Wrapper):
            return value.raw
        else:
            return value
    
    def __getitem__(self, key):
        return self._wrap(self.raw.__getitem__(key))
    def __setitem__(self, key, value):
        return self.raw.__setitem__(key, self._unwrap(value))
    def __delitem__(self, key):
        return self.raw.__delitem__(key)
    # TODO isn't there some mixin class somewhere in the standard library to implement all the remaining list methods?
    def append(self, value):
        return self.raw.append(self._unwrap(value))
    def pop(self, *args):
        return self._wrap(self.raw.pop(*args))

class WrappedProperty:
    """
    This is a special type of property designed to work in conjunction with the ``Wrapper`` class 
    to automatically wrap values from ``raw``.
    """
    def __init__(self, key, wrapper, default=None, inheritable=False):
        self.default = default
        self.key = key
        self.wrapper = wrapper
        self.inheritable = inheritable
    
    def _wrap(self, instance, value):
        if isinstance(self.wrapper, type) and issubclass(self.wrapper, Wrapper):
            return self.wrapper(instance.pdf, value)
        else:
            return self.wrapper(value)
    
    def _unwrap(self, value):
        if isinstance(value, Wrapper):
            return value.raw
        else:
            return value

    def __get__(self, instance:Wrapper, owner):
        if self.inheritable:
            raw = instance.raw.inheritable
        else:
            raw = instance.raw
        try:
            to_wrap = raw[self.key]
        except KeyError:
            return self.default
        return self._wrap(instance, to_wrap)
    
    def __set__(self, instance:Wrapper, value):
        if self.inheritable:
            raw = instance.raw.inheritable
        else:
            raw = instance.raw
        raw[self.key] = self._unwrap(value)

    def __delete__(self, instance):
        try:
            del instance.raw[self.key]
        except KeyError:
            pass


class WrappedArrayProperty(WrappedProperty):
    def __init__(self, key, contained_wrapper):
        super().__init__(key, ArrayWrapper)
        self.contained_wrapper = contained_wrapper
    
    def _wrap(self, instance, value):
        return ArrayWrapper(instance.pdf, value, self.contained_wrapper)
    