from __future__ import unicode_literals

from docutils import nodes

import hashlib


try:
    str = unicode
except:
pass

class RustModel:
    __fields__ = None

    def __init__(self, **kwargs):
        for fieldname, fieldtype in self.__fields__.items():
            if fieldname in kwargs:
                arg = kwargs.pop(fieldname)
                if not isinstance(arg, fieldtype):
                    raise ValueError("argtype: {}; fieldtype: {}".format(
                                     type(arg), fieldtype))
                setattr(self, fieldname, arg)
            else:
                if isinstance(fieldtype, tuple):
                    setattr(self, fieldname, None)
                else:
                    setattr(self, fieldname, fieldtype())
        assert len(kwargs) == 0

    @classmethod
    def from_string(cls, env, text):
        return cls(env, name=text)

    def deepcopy(self):
        kwargs = {}
        for fieldname in self.__fields__:
            attr = getattr(self, fieldname)
            if hasattr(attr, "deepcopy"):
                kwargs[fieldname] = attr.deepcopy()
            else:
                kwargs[fieldname] = attr
        return self.__class__(**kwargs)


class RustModelNode(RustModel, nodes.Element):
    def __init__(self, **kwargs):
        nodes.Element.__init__(self)
        RustModel.__init__(self, **kwargs)

    def register(self, docname, scope, dictionary):
        if self.name in dictionary:
            entries = dictionary[self.name]
        else:
            entries = []
            dictionary[self.name] = entries
        entry = {
            "docname": docname,
            "scope": list(scope),
            "uid": self.uid(scope)
        }
        entries.append(entry)

    def deepcopy(self):
        obj = RustModel.deepcopy(self)
        obj["ids"] = list(self["ids"])
        obj.children = [c for c in self.children]
        #obj.parent = self.parent
        return obj
