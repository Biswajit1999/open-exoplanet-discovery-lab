import numpy as np

from exolab.crossmatch import angular_separation_arcsec, nearest_match


def test_zero_coordinate_separation():
    value = angular_separation_arcsec(120.0, -20.0, 120.0, -20.0)
    assert np.isclose(float(value), 0.0)


def test_nearest_match_obeys_radius():
    result = nearest_match(
        10.0,
        20.0,
        [10.0001, 11.0],
        [20.0001, 20.0],
        max_separation_arcsec=2.0,
    )
    assert result is not None
    assert result[0] == 0
    assert result[1] < 2.0
