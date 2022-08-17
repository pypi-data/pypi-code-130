from nzshm_common.grids import load_grid


def test_load_wlg_0_005():
    assert len(load_grid('WLG_0_05_nb_1_1')) == 62


def test_load_wlg_0_001():
    assert len(load_grid('WLG_0_01_nb_1_1')) == 764


def test_load_nz_0_1():
    assert len(load_grid('NZ_0_1_NB_1_1')) == 3741


def test_load_lat_lon_order_spacing():
    """Corordinate order must be lat, lon."""
    grid = load_grid('NZ_0_1_NB_1_0')
    assert grid[0] == (-46.1, 166.4)
    assert grid[1] == (-46.0, 166.4)

    grid = load_grid('NZ_0_1_NB_1_1')
    assert grid[0] == (-46.1, 166.4)
    assert grid[1] == (-46.0, 166.4)

    grid = load_grid('NZ_0_2_NB_1_1')
    assert grid[0] == (-46.4, 166.6)
    assert grid[1] == (-46.2, 166.6)

    grid = load_grid('WLG_0_05_nb_1_1')
    assert grid[0] == (-41.4, 174.65)
    assert grid[1] == (-41.35, 174.65)
    assert grid[2] == (-41.3, 174.65)

    grid = load_grid('WLG_0_01_nb_1_1')
    assert grid[0] == (-41.36, 174.69)
    assert grid[1] == (-41.35, 174.69)
    assert grid[2] == (-41.34, 174.69)
