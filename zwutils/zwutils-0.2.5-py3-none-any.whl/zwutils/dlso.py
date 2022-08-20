'''
(d)ict (l)ist (s)et (o)bject) utils
'''
import collections
from operator import itemgetter
from itertools import groupby
from inspect import ismethod, isbuiltin
from functools import reduce

class ZWObject(object):
    def as_dict(self):
        return obj2dict(self)
    
    @classmethod
    def from_dict(cls, kv):
        return extend_attrs(None, kv)
    
    def __iter__(self):
        self._keys = list(obj2dict(self).keys())
        self._keycur = 0 if self._keys else None
        return self
    
    def __next__(self):
        if self._keycur is None or self._keycur > len(self._keys)-1:
            raise StopIteration
        val = getattr(self, self._keys[self._keycur])
        self._keycur += 1
        return val

def _ismethod(o):
    return ismethod(o) or isbuiltin(o)

def getflds(o):
    return [s for s in dir(o) if \
        not s.startswith('_') and \
        not _ismethod(getattr(o, s))
    ]

def dict2obj(kv):
    """Transfer dict to ZWObject,  dict will be transfer iterately.

    :param dict kv: dict object
    :return: object
    :rtype: ZWObject

    .. code-block:: python
        :linenos:

        r = dlso.dict2obj({
            's': 's',
            'n': 1,
            'list': [1, '2'],
            'dict': {'a1':'a1', 'a2':'a2', 'sub1':{'b1':'b1'}},
            'none': None,
            'obj': type('', (), {'a3': 'a3', 'sub2': type('', (),{'b2':'b2'})()})(),
            'zwo': dlso.ZWObject({'a4':'a4'}),
        })
        assert r.s == 's' and r.none == None
        assert r.dict.a1 == 'a1' and r.dict.sub1.b1 == 'b1'
        assert r.obj.a3 == 'a3' and r.obj.sub2.b2 == 'b2'
    """
    kv = kv or {}
    o = ZWObject()
    for k, v in kv.items():
        if isinstance(kv[k], dict):
            setattr(o, k, dict2obj(kv[k]))
        elif not _ismethod(kv[k]):
            setattr(o, k, v)
    return o

_builtin_types = [type(None), bool, int, float, complex, list, tuple, range, str, bytes, bytearray, memoryview, set, frozenset, dict]
def obj2dict(o):
    """Transfer object to dict and ignore hidden/method attribute. Object will be transfer iterately.

    :param object o: object
    :return: dict
    :rtype: dict

    .. code-block:: python
        :linenos:

        r = dlso.obj2dict(type('', (), {
            's': 's',
            'n': 1,
            'list': [1, '2'],
            'dict': {'a1':'a1', 'a2':'a2', 'sub1':{'b1':'b1'}},
            'none': None,
            'obj': type('', (), {'a3': 'a3', 'sub2': type('', (),{'b2':'b2'})()})(),
            'zwo': dlso.ZWObject({'a4':'a4'}),
        })())
        assert r['s'] == 's' and r['none'] == None
        assert r['dict']['a1'] == 'a1' and r['dict']['sub1']['b1'] == 'b1'
        assert r['obj']['a3'] == 'a3' and r['obj']['sub2']['b2'] == 'b2'
    """
    o = o or ZWObject()
    r = {}
    attrs = getflds(o)
    for attr in attrs:
        val = getattr(o, attr)
        if any([isinstance(val, t) for t in _builtin_types]):
            r[attr] = val
        else:
            r[attr] = obj2dict(val)
    return r

def arrs2recs(h, rs):
    """Transfer Header list and Data list to Dict list(Record list).
    
    :param list h: Header list
    :param list[list] rs: Data list
    :return: list[dict]: Dict list
    :rtype: list

    .. code-block:: python
        :linenos:

        recs = dlso.arrs2recs(['hdr_a','hdr_b'], [['a', 'b'], ['c', 'd']])
        assert recs == [{'hdr_a':'a', 'hdr_b':'b'}, {'hdr_a':'c', 'hdr_b':'d'}]
    """
    return [dict(zip(h, r)) for r in rs]

def extend_attrs(o, dat):
    """Extend/Update attrs of object by dict/object if attr not exist/exist in object.
    
    :param object o: dest object
    :param dict/object dat: value to extend/update
    :return: object
    :rtype: object/ZWObject

    .. code-block:: python
        :linenos:

        o = type('', (), {'a1':'a1', 'a2':'a2'})()
        o = dlso.extend_attrs(o, {'a2':'n2', 'b1':'b1', 'sub1': {'c1': 'c1'}})
        assert o.a1 == 'a1' and o.a2 == 'n2' and o.b1 == 'b1' and o.sub1.c1 == 'c1'
    """
    o = o or ZWObject()
    d = dat or ZWObject()
    o = dict2obj(o) if isinstance(o, dict) else o
    d = dict2obj(d) if isinstance(d, dict) else d
    attrs = getflds(d)
    for attr in attrs:
        setattr(o, attr, getattr(d, attr))
    return o

def update_attrs(o, dat):
    """Update attrs of object by dict/object without adding new attrs.
    
    :param object o: dest object
    :param dict/object dat: value to update
    :return: object
    :rtype: object/ZWObject

    .. code-block:: python
        :linenos:

        o = type('', (), {'a1':'a1', 'a2':'a2'})()
        o = dlso.update_attrs(o, {'a2':'n2', 'b1':'b1', 'sub1': {'c1': 'c1'}})
        assert o.a1 == 'a1' and o.a2 == 'n2' and not hasattr(o, 'b1') and not hasattr(o, 'sub1')
    """
    o = o or ZWObject()
    d = dat or ZWObject()
    o = dict2obj(o) if isinstance(o, dict) else o
    d = dict2obj(d) if isinstance(d, dict) else d
    attrs = getflds(d)
    for attr in attrs:
        if hasattr(o, attr):
            setattr(o, attr, getattr(d, attr))
    return o

def upsert_config(pcfg, dcfg, ncfg, acfg):
    """acfg overwirte ncfg overwirte dcfg overwirte pcfg
    
    :param dict/object pcfg: parent cfg
    :param dict/object dcfg: default cfg
    :param dict/object ncfg: new cfg
    :param dict/object acfg: param cfg
    :return: pcfg updated
    :rtype: object/ZWObject

    .. code-block:: python
        :linenos:

        pcfg = dlso.ZWObject.from_dict({'p1': 'p1', 'p2':'p2'})
        dcfg = {'p1': 'dp1', 'd1': 'd1', 'sub1': {'c1': 'c1'}}
        ncfg = {'p2': 'np2', 'd1': 'nd1', 'n1': 'n1'}
        acfg = {'a1': 'a1', 'n1': 'an1'}
        o = dlso.upsert_config(pcfg, dcfg, ncfg, acfg)
        assert id(o) == id(pcfg) and o.p1 == 'dp1' and o.p2 == 'np2' and o.d1 == 'nd1' and o.n1 == 'an1'
        assert o.sub1.c1 == 'c1'
    """
    # pcfg = parent_cfg or type('', (), {})()
    pcfg = pcfg or ZWObject()
    dcfg = dcfg or ZWObject()
    ncfg = ncfg or ZWObject()
    acfg = acfg or {}
    pcfg = extend_attrs(extend_attrs(extend_attrs(pcfg, dcfg), ncfg), acfg)
    return pcfg

def listinter(a, b):
    """Get intersection from two list

    :param list a: left list
    :param list b: right list
    :return: result list
    :rtype: list

    .. code-block:: python
        :linenos:

        >>> listinter([0,1,3,2], [2,3,4,5])
        [3,2]
    """
    return list(set(a).intersection(b)) # choose smaller to a or b?

def listsplit(arr, siz):
    """Split list into several parts.

    :param list arr: list to split
    :param int siz: sublist size
    :return: 2D list
    :rtype: list

    .. code-block:: python
        :linenos:

        >>> listsplit([0,1,2,3,4,5,6], 3)
        [ [0,1,2], [3,4,5], [6] ]
    """
    arrlen = len(arr)
    step = int(arrlen / siz) + 1
    rtn = [arr[i:i+step] for i in range(0, arrlen, step)]
    return rtn

def listunify(arr, keyfunc=None):
    """Unify dict list,

    :param list[dict] arr: dict list to unify
    :return: unified list
    :rtype: list[dict]

    .. code-block:: python
        :linenos:

        >>> dlso.listunify([{'a': 1}, {'a': 1}, {'a': 3}, {'b': 4}])
        [{'a': 1}, {'a': 3}, {'b': 4}]

        >>> dlso.listunify([{'a': 1, 'b': 3}, {'a': 2, 'b': 3}, {'a': 3}, {'b': 4}], keyfunc=lambda x, y: 'b' in y and y['b'] not in {o['b'] for o in x} )
        [{'a': 1, 'b': 3}, {'b': 4}]
    """
    keyfunc = keyfunc or (lambda x, y: y not in x)
    return reduce(lambda x, y: x + [y] if keyfunc(x, y) else x, [[], ] + arr)

def listcmp(a, b):
    """
        .. code-block:: python
            :linenos:

            assert False == dlso.listcmp([1,2,3,3], [1,2,2,3])
            assert True == dlso.listcmp([1,2,3], [2,1,3])
    """
    compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
    return compare(a, b)

def listgroupby(arr, key, copy=False):
    """Group by dict list by fld/keyfunc

    :param list[dict] arr: dict list to group
    :param function/fieldname key: 
    :param bool copy: return new list or not
    :return: result list
    :rtype: list[dict]

    .. code-block:: python
        :linenos:

        arr = [
            {'flda':'a', 'fld':'a'},
            {'flda':'b', 'fld':'a'},
            {'flda':'b', 'fld':'b'},
        ]
        r = dlso.listgroupby(arr, 'fld')
        assert r[0] == ('a', [{'flda': 'a', 'fld': 'a'}, {'flda': 'b', 'fld': 'a'}])
        assert r[1] == ('b', [{'flda': 'b', 'fld': 'b'}])

    """
    arr = arr[:] if copy else arr
    arr.sort(key=itemgetter(key))
    grp = groupby(arr, itemgetter(key))
    return [(key, list(group)) for key, group in grp]
