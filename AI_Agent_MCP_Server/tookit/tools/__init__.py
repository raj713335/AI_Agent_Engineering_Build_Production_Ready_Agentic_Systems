# toolkit/tools/__init__.py
from importlib import import_module as _im
from ._discover import find_tools as _ft

_tools_cache = None


def get_tools():
    global _tools_cache
    if _tools_cache is None:
        _tools_cache = _ft(_im(__name__))
    return _tools_cache


# Python ≥3.7: expose attribute lazily
def __getattr__(name):
    if name == "tools":
        return get_tools()
    raise AttributeError(name)
