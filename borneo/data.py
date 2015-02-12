from __future__ import absolute_import

try:
    import cPickle as pickle
except ImportError:
    import pickle

from borneo.paths import make_results_path


def pickle_result(filename, data, study):
    """Pickle the supplied data to the specified file in the given study results
    directory"""
    with open(make_results_path(filename, study), 'w') as f:
        pickle.dump(data, f, protocol=2)


def unpickle_result(filename, study):
    """Load the data from the specified file in the given study results
    directory"""
    with open(make_results_path(filename, study)) as f:
        data = pickle.load(f)
    return data
