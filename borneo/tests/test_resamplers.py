from __future__ import absolute_import

import numpy as np

from borneo.resamplers import (bootstrap, bootstrap_error,
                               jackknife, jackknife_error)


def test_jackknife():
    """Test jackknife"""
    data = [1.0, 2.0, 3.0]
    assert jackknife(data) == [2.5, 2.0, 1.5]


def test_jackknife_error():
    """Test jackknife"""
    data = [1.0, 2.0, 3.0]
    assert np.allclose(jackknife_error(data), 1.1547005383792517)


def test_bootstrap():
    """Test bootstrap"""
    data = [1.0, 2.0, 3.0]
    bins = [[0, 1, 0], [1, 2, 0], [0, 2, 2]]
    resampled_data, new_bins = bootstrap(data, bins=bins)
    assert resampled_data == [4.0 / 3.0, 2.0, 7.0 / 3.0]
    assert new_bins == bins


def test_bootstrap_error():
    """Test bootstrap"""
    data = [1.0, 2.0, 3.0]
    assert np.allclose(bootstrap_error(data), np.std(data))