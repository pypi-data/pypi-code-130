from nzshm_common import location


def test_location_keys_unique():
    assert len(location.LOCATIONS) == len(set(loc['id'] for loc in location.LOCATIONS))


def test_location_rot():
    rot = location.LOCATIONS_BY_ID['ROT']
    assert rot['name'] == 'Rotorua'
