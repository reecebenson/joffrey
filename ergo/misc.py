import inspect
from functools import wraps
from itertools import zip_longest
from types import SimpleNamespace


def typecast(func):
    params = inspect.signature(func).parameters.items()
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not params:
            return func(*args, **kwargs)
        # Prepare list/dict of all positional/keyword args with annotation or None
        pos_annot, kw_annot = (
          [func.__annotations__[p.name] for _, p in params if p.kind < 3 and p.name in func.__annotations__],
          {p.name if p.kind == 3 else None: func.__annotations__.get(p.name) for _, p in params if p.kind >= 3}
          )
        # Assign default to handle **kwargs annotation if not given/callable
        if not callable(kw_annot.get(None)):
            kw_annot[None] = lambda x: x
        # zip_longest to account for any var_positional argument
        fill = zip_longest(pos_annot, args, fillvalue=pos_annot[-1] if pos_annot else None)
        return func(
          *(hint(val) if callable(hint) else val for hint, val in fill),
          **{a: kw_annot[a](b) if a in kw_annot and callable(kw_annot[a]) else kw_annot[None](b) for a, b in kwargs.items()}
          )
    return wrapper


def multiton(pos=None, *, kw):
    def make_multiton(cls, *, classes={}):
        if cls not in classes:
            classes[cls] = {}
        instances = classes[cls]
        
        @wraps(cls)
        def getinstance(*args, **kwargs):
            key = (args[:pos], kwargs) if kw else args[:pos]
            if key not in instances:
                instances[key] = cls(*args, **kwargs)
            return instances[key]
        return getinstance
    return make_multiton


class ErgoNamespace(SimpleNamespace):
    def __bool__(self):
        return bool(vars(self))
    
    def __contains__(self, name):
        return hasattr(self, name)
    
    def __getitem__(self, name):
        return self.__getattribute__(name)
    
    def __iter__(self):
        yield from vars(self)
    
    def items(self):
        return vars(self).items()
    
    def keys(self):
        return vars(self).keys()
    
    def values(self):
        return vars(self).values()