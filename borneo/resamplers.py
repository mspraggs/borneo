from __future__ import absolute_import
from __future__ import division

import numpy as np


def bin_data(data, binsize=1):
    """Bins the supplied data into bins of the specified size"""

    return [sum(data[i:i+binsize]) / binsize
            for i in range(0, len(data) - binsize + 1, binsize)]


def jackknife(data):
    """Perform a jackknife resample on the specified data"""
    N = len(data)
    data_sum = sum(data)
    return [(data_sum - datum) / (N - 1) for datum in data]


def jackknife_error(data, centre=None):
    """Compute the jackknife error of the supplied dataset, using the supplied
    central value if it's specified"""
    N = len(data)
    centre = centre if centre is not None else sum(data) / len(data)
    deviations = [(datum - centre)**2 for datum in data]
    return ((N - 1) / N * sum(deviations))**0.5


def bootstrap(data, num_bootstraps=None, bins=None):
    """Perform a bootstrap resample on the specified data"""
    N = len(data)
    if not bins:
        bins = [np.random.randint(N, size=N).tolist()
                for i in range(num_bootstraps)]
    resampled_data = [sum([data[i] for i in sample_bins]) / N
                      for sample_bins in bins]
    return resampled_data, bins


def bootstrap_error(data, centre=None):
    """Compute the jackknife error of the supplied dataset, using the supplied
    central value if it's specified"""
    N = len(data)
    centre = centre or sum(data) / len(data)
    deviations = [(datum - centre)**2 for datum in data]
    return (1 / N * sum(deviations))**0.5
