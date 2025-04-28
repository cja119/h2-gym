"""

"""
from re import sub as re_sub

def get_rang(graph, _vars):
    if _vars is None:
        return None
    
    _rngs = {}
    for targ in _vars:
        if targ not in _rngs:
            _rngs[targ] = {}
        for val in _vars[targ]:
            _rngs[targ][val] \
                = graph[re_sub(r"[+]","",targ)]['variables']\
                    .get_rng(val)
    return _rngs