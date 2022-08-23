# -*- coding: utf-8 -*-
from hao import places


def get_provinces():
    return [place.name for place in places.PLACES]


def get_cities():
    city_list = []
    for place in places.PLACES:
        if place.children is None or place.children_type is None or place.children_type != places.TYPE_CITY:
            continue

        for child in place.children:
            city = child.name
            city_list.append(city)
    return city_list


def get_provinces_and_cities():
    return get_provinces() + get_cities()
