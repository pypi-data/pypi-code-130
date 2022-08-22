from typing import List, Any

from nextkg_api.data_models import Property


def merge_properties(properties: List[Property], other_properties: List[Property]) -> List[Property]:
    props = {}
    for i, p in enumerate(properties):
        props[p.name] = (i, p)
    for p in other_properties:
        if p.name in props:
            _i, _p = props[p.name]
            props[p.name] = (_i, Property(
                name=_p.name,
                value=_merge_property_values(_p.value, p.value),
                json_value=_merge_property_values(_p.json_value, p.json_value),
            ))
        else:
            props[p.name] = (len(props), Property(
                name=p.name,
                value=p.value,
                json_value=p.json_value,
            ))
    a = [i for i in props.values()]
    a.sort(key=lambda x: x[0])
    return [i[1] for i in a]


def _merge_property_values(values: List[Any], other_values: List[Any]) -> List[Any]:
    if values:
        if not isinstance(values, list):
            values = [values]
        s = set(values)
        result = list(values)
    else:
        s = set()
        result = []
    if other_values:
        if not isinstance(other_values, list):
            other_values = [other_values]
        for v in other_values:
            if v not in s:
                result.append(v)
    return result
