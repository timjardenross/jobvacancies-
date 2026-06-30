import sys, os

_root = os.path.dirname(os.path.abspath(__file__))
_src  = os.path.join(_root, "src")

for _p in (_root, _src):
    if _p not in sys.path:
        sys.path.insert(0, _p)
