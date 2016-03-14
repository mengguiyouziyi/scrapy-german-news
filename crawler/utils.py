# -*- coding: utf-8 -*-
# Utils for crawler project

def get_first(iterable, default=None):
    """Get first element of list or None (Used for single element lists)"""
    if iterable:
        if len(iterable) > 0:
            return iterable[0].encode('utf-8')
    return None
